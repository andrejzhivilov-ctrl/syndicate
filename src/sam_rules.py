"""A small, safe rule language for Sam's strategies (Andrii, 20.11.2026: Sam tests, changes and creates his own).

A strategy is data, not code: its entry and stop are expressions over candles, such as
``cross_up(ema(close, 20), ema(close, 55)) and rsi(close, 14) > 50``. The expression is parsed with
:mod:`ast` and only the names, functions and operators listed here are accepted, so a strategy Sam
writes can never run arbitrary Python in the trading engine. Every function works on a whole pandas
series, so the same rule serves the live tournament (last closed bar) and the backtest (every bar).

Bars: ``open high low close volume``. Functions (``n`` is a whole number from 1 to MAX_PERIOD):

- ``ema(x, n)``, ``sma(x, n)``, ``std(x, n)``: moving average and deviation.
- ``rsi(x, n)``, ``atr(n)``: Wilder's RSI, average true range.
- ``highest(x, n)``, ``lowest(x, n)``: extreme of the n bars *before* this one (a breakout compares with them).
- ``shift(x, n)``: the value n bars ago. ``abs(x)``.
- ``cross_up(a, b)``, ``cross_down(a, b)``: a crossed b on this bar.
- ``day_high()``, ``day_low()``: the previous UTC day's high and low.
"""
from __future__ import annotations

import ast
from typing import Any, Callable, Dict, Optional, Set

import numpy as np
import pandas as pd

MAX_PERIOD = 250
MAX_CHARS = 400
BARS = ("open", "high", "low", "close", "volume")


class RuleError(ValueError):
    """The expression is outside the language; the message says what to change."""


def atr(frame: pd.DataFrame, n: int = 14) -> pd.Series:
    prev = frame["close"].shift()
    true_range = pd.concat([frame["high"] - frame["low"], (frame["high"] - prev).abs(), (frame["low"] - prev).abs()],
                           axis=1)
    return true_range.max(axis=1).rolling(n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, float("nan")))


def _day_extreme(frame: pd.DataFrame, column: str, how: str) -> pd.Series:
    days = pd.Series(frame.index.date, index=frame.index)
    per_day = frame[column].groupby(days.values).agg(how)
    previous = per_day.shift(1)
    return pd.Series(days.map(previous).astype(float).values, index=frame.index)


def _cross(a: pd.Series, b: pd.Series, up: bool) -> pd.Series:
    diff = a - b
    before = diff.shift(1)
    hit = (before <= 0) & (diff > 0) if up else (before >= 0) & (diff < 0)
    return hit.fillna(False)


def _period(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or int(value) != value:
        raise RuleError("period must be a whole number")
    n = int(value)
    if not 1 <= n <= MAX_PERIOD:
        raise RuleError(f"period must be from 1 to {MAX_PERIOD}")
    return n


def _series(value: Any, frame: pd.DataFrame) -> pd.Series:
    if isinstance(value, pd.Series):
        return value
    return pd.Series(float(value), index=frame.index)


#: name -> (arity, implementation(frame, *args)). Periods are checked before use.
FUNCTIONS: Dict[str, Any] = {
    "ema": (2, lambda f, x, n: _series(x, f).ewm(span=_period(n)).mean()),
    "sma": (2, lambda f, x, n: _series(x, f).rolling(_period(n)).mean()),
    "std": (2, lambda f, x, n: _series(x, f).rolling(_period(n)).std()),
    "rsi": (2, lambda f, x, n: rsi(_series(x, f), _period(n))),
    "atr": (1, lambda f, n: atr(f, _period(n))),
    "highest": (2, lambda f, x, n: _series(x, f).shift(1).rolling(_period(n)).max()),
    "lowest": (2, lambda f, x, n: _series(x, f).shift(1).rolling(_period(n)).min()),
    "shift": (2, lambda f, x, n: _series(x, f).shift(_period(n))),
    "abs": (1, lambda f, x: _series(x, f).abs()),
    "cross_up": (2, lambda f, a, b: _cross(_series(a, f), _series(b, f), True)),
    "cross_down": (2, lambda f, a, b: _cross(_series(a, f), _series(b, f), False)),
    "day_high": (0, lambda f: _day_extreme(f, "high", "max")),
    "day_low": (0, lambda f: _day_extreme(f, "low", "min")),
}
#: Which argument is the look-back period: it must be a whole number written in the rule.
PERIOD_ARG = {"ema": 1, "sma": 1, "std": 1, "rsi": 1, "highest": 1, "lowest": 1, "shift": 1, "atr": 0}
_BINARY: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
}
_COMPARE: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Lt: lambda a, b: a < b, ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b,
}


def parse(text: Any) -> ast.Expression:
    """The checked syntax tree of one rule; RuleError names the first thing outside the language."""
    if not isinstance(text, str) or not text.strip():
        raise RuleError("rule must be a non-empty text")
    if len(text) > MAX_CHARS:
        raise RuleError(f"rule is longer than {MAX_CHARS} characters")
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except SyntaxError as exc:
        raise RuleError(f"syntax error: {exc.msg}") from None
    for node in ast.walk(tree):
        _check(node)
    return tree


def _check(node: ast.AST) -> None:
    allowed = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.BinOp,
               ast.Compare, ast.Call, ast.Name, ast.Load, ast.Constant, *_BINARY, *_COMPARE)
    if not isinstance(node, allowed):
        raise RuleError(f"{type(node).__name__} is not allowed")
    if isinstance(node, ast.Name) and node.id not in BARS and node.id not in FUNCTIONS:
        raise RuleError(f"unknown name {node.id!r}; bars: {', '.join(BARS)}")
    if isinstance(node, ast.Constant) and (isinstance(node.value, bool) or not isinstance(node.value, (int, float))):
        raise RuleError("only numbers may be written as constants")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
            raise RuleError(f"unknown function; available: {', '.join(sorted(FUNCTIONS))}")
        if node.keywords or len(node.args) != FUNCTIONS[node.func.id][0]:
            raise RuleError(f"{node.func.id} takes {FUNCTIONS[node.func.id][0]} arguments")
        if node.func.id in PERIOD_ARG:
            arg = node.args[PERIOD_ARG[node.func.id]]
            if not isinstance(arg, ast.Constant):
                raise RuleError(f"{node.func.id}: the period must be a number written in the rule")
            _period(arg.value)


def longest_period(text: str) -> int:
    """The longest look-back in a rule: the bars it needs before its first honest answer."""
    numbers = [int(n.value) for n in ast.walk(parse(text)) if isinstance(n, ast.Constant) and float(n.value).is_integer()
               and 1 <= n.value <= MAX_PERIOD]
    uses_day = any(isinstance(n, ast.Name) and n.id in ("day_high", "day_low") for n in ast.walk(parse(text)))
    return max(numbers + [14]) + (24 if uses_day else 0)


def evaluate(text: str, frame: pd.DataFrame) -> pd.Series:
    """The rule on every bar: booleans for an entry, prices for a stop."""
    tree = parse(text)
    with np.errstate(all="ignore"):
        result = _eval(tree.body, frame)
    return _series(result, frame)


def _eval(node: ast.AST, frame: pd.DataFrame) -> Any:
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id in BARS:
            return frame[node.id].astype(float)
        raise RuleError(f"{node.id} is a function: write {node.id}(...)")
    if isinstance(node, ast.Call):
        _arity, impl = FUNCTIONS[node.func.id]  # type: ignore[union-attr]
        args = [_eval(a, frame) if not isinstance(a, ast.Constant) else a.value for a in node.args]
        return impl(frame, *args)
    if isinstance(node, ast.BinOp):
        return _BINARY[type(node.op)](_eval(node.left, frame), _eval(node.right, frame))
    if isinstance(node, ast.UnaryOp):
        value = _eval(node.operand, frame)
        return -value if isinstance(node.op, ast.USub) else ~_bool(value, frame)
    if isinstance(node, ast.BoolOp):
        values = [_bool(_eval(v, frame), frame) for v in node.values]
        out = values[0]
        for value in values[1:]:
            out = (out & value) if isinstance(node.op, ast.And) else (out | value)
        return out
    if isinstance(node, ast.Compare):
        left, out = _eval(node.left, frame), None
        for op, right_node in zip(node.ops, node.comparators):
            right = _eval(right_node, frame)
            part = _bool(_COMPARE[type(op)](_series(left, frame), right), frame)
            out = part if out is None else out & part
            left = right
        return out
    raise RuleError(f"{type(node).__name__} is not allowed")


def _bool(value: Any, frame: pd.DataFrame) -> pd.Series:
    series = _series(value, frame)
    if series.dtype != bool:
        series = series.fillna(0).astype(bool)
    return series


def names_used(text: str) -> Set[str]:
    return {n.id for n in ast.walk(parse(text)) if isinstance(n, ast.Name)}


def check(text: Optional[str]) -> Optional[str]:
    """None when the rule is inside the language, otherwise the reason."""
    if text is None:
        return None
    try:
        parse(text)
    except RuleError as exc:
        return str(exc)
    return None
