"""Sam's strategy catalog: in the repository, on the server and in the Second Brain (Andrii, 20.11.2026).

- **Repository:** ``sam_core/strategies/*.json`` — the strategies Andrii, Claude or a source brought in.
- **Server:** ``<EVA_DATA_DIR>/sam_strategies/`` — the strategies Sam wrote himself (``specs/``) and
  ``state.json`` with every strategy's status, its last backtest and the full history of changes.
- **Second Brain:** ``Сем/Стратегії/<id>.md`` — a card per strategy and ``Каталог.md``, rewritten on
  every change, so nothing Sam tried is lost and Obsidian search finds it.

A strategy is data (src/sam_rules.py), never code. Its life: ``idea`` → backtest → ``paper`` when the
gate in src/sam_backtest.py passes, or ``rejected`` with the reasons → ``archived`` when it stops
working. Nothing is deleted: a change is a new strategy with ``parent`` pointing at the old one.
``candidate`` (a step towards real money) is set only by Andrii; Sam's tool refuses it.
"""
from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

import structlog

from src import sam_backtest, sam_rules
from src.data_paths import ensure_dir

logger = structlog.get_logger(__name__)

SEED_DIR = Path(__file__).resolve().parents[1] / "sam_core" / "strategies"
STATUSES = ("idea", "rejected", "paper", "candidate", "archived")
AUTHORS = ("andrii", "sam", "claude", "codex", "external")
TIMEFRAMES = ("1m", "5m", "15m", "30m", "1h", "4h", "1d")
STYLES = ("scalp", "day", "mid", "long")
MARKETS = ("crypto", "trading")
MAX_RISK = 0.01
MIN_RR = 2.5
#: Paper strategies running at once; more ideas wait as ``idea`` so the five-minute pass stays light.
MAX_PAPER = 25
ID = re.compile(r"^[a-z0-9_]{3,48}$")
BACKTEST_BARS = 3_000
CARD_DIR = ("Сем", "Стратегії")
_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _root() -> Path:
    return ensure_dir("sam_strategies")


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    spare = path.with_suffix(".tmp")
    spare.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    spare.replace(path)


def seeds() -> Dict[str, Dict[str, Any]]:
    return {p.stem: _read_json(p, {}) for p in sorted(SEED_DIR.glob("*.json"))}


def own() -> Dict[str, Dict[str, Any]]:
    return {p.stem: _read_json(p, {}) for p in sorted((_root() / "specs").glob("*.json"))}


def state() -> Dict[str, Any]:
    return _read_json(_root() / "state.json", {})


def specs() -> Dict[str, Dict[str, Any]]:
    """Every strategy: the repository's first, then Sam's own (an id is never shared)."""
    return {**own(), **seeds()}


def status_of(sid: str, spec: Optional[Mapping[str, Any]] = None, saved: Optional[Mapping[str, Any]] = None) -> str:
    saved = state() if saved is None else saved
    spec = specs().get(sid, {}) if spec is None else spec
    return (saved.get(sid) or {}).get("status") or spec.get("status") or "idea"


def _choice(spec: Mapping[str, Any], key: str, allowed: Tuple[str, ...]) -> List[str]:
    return [] if spec.get(key) in allowed else [f"{key}: один з {', '.join(allowed)}"]


def _numbers(spec: Mapping[str, Any]) -> List[str]:
    problems = []
    markets = spec.get("markets")
    if not isinstance(markets, list) or not markets or any(m not in MARKETS for m in markets):
        problems.append(f"markets: список з {', '.join(MARKETS)}")
    risk, rr = spec.get("risk"), spec.get("rr", MIN_RR)
    if not isinstance(risk, (int, float)) or not 0 < risk <= MAX_RISK:
        problems.append(f"risk: частка рахунку від 0 до {MAX_RISK}")
    if not isinstance(rr, (int, float)) or rr < MIN_RR:
        problems.append(f"rr: щонайменше {MIN_RR} (правило Андрія)")
    return problems


def _rules(spec: Mapping[str, Any]) -> List[str]:
    if not spec.get("long") and not spec.get("short"):
        return ["потрібне правило long або short"]
    problems = []
    for side in ("long", "short"):
        for key in ((side, f"stop_{side}") if spec.get(side) else ()):
            why = sam_rules.check(spec.get(key)) if spec.get(key) else "правило стопу обов'язкове"
            if why:
                problems.append(f"{key}: {why}")
    return problems


def validate(spec: Mapping[str, Any]) -> List[str]:
    """Every problem with a spec, in words Sam can act on; empty when it may enter the catalog."""
    problems = [] if ID.match(str(spec.get("id", ""))) else ["id: 3–48 малих латинських літер, цифр або _"]
    if not str(spec.get("title", "")).strip() or not str(spec.get("hypothesis", "")).strip():
        problems.append("title і hypothesis обов'язкові: чому стратегія має працювати")
    for key, allowed in (("author", AUTHORS), ("timeframe", TIMEFRAMES), ("style", STYLES)):
        problems += _choice(spec, key, allowed)
    return problems + _numbers(spec) + _rules(spec)


def _event(saved: Dict[str, Any], sid: str, status: str, why: str, by: str, backtest: Optional[Dict] = None) -> None:
    row = saved.setdefault(sid, {"history": []})
    row.setdefault("history", []).append({"at": _now(), "from": row.get("status"), "to": status, "why": why, "by": by})
    row["status"] = status
    if backtest is not None:
        row["backtest"] = {"at": _now(), **backtest}


def set_status(sid: str, status: str, why: str, by: str) -> Dict[str, Any]:
    if status not in STATUSES:
        return {"status": "error", "error": "unknown_status", "available": list(STATUSES)}
    if sid not in specs():
        return {"status": "error", "error": "unknown_strategy"}
    if status == "candidate" and by != "andrii":
        return {"status": "refused", "reason": "needs_andrii",
                "detail": "Кандидата на реальні гроші обирає лише Андрій."}
    with _LOCK:
        saved = state()
        _event(saved, sid, status, why, by)
        _write_json(_root() / "state.json", saved)
    write_cards()
    return {"status": "ok", "id": sid, "now": status}


def propose(spec: Dict[str, Any], by: str = "sam") -> Dict[str, Any]:
    """A new strategy enters as ``idea``; changing one is a new id with ``parent``."""
    spec = {**spec, "author": spec.get("author") or by, "created": _now()[:10]}
    spec.setdefault("rr", MIN_RR)
    spec.pop("status", None)
    problems = validate(spec)
    if spec.get("id") in specs():
        problems.append("такий id уже є: зміна — це нова стратегія з parent")
    if spec.get("parent") and spec["parent"] not in specs():
        problems.append("parent: такої стратегії немає")
    if problems:
        return {"status": "error", "error": "invalid_strategy", "problems": problems,
                "language": sam_rules.__doc__.split("\n\n", 2)[-1]}
    spec["min_bars"] = int(spec.get("min_bars") or max(sam_rules.longest_period(spec[k]) for k in
                                                       ("long", "short", "stop_long", "stop_short") if spec.get(k)) + 10)
    with _LOCK:
        _write_json(_root() / "specs" / f"{spec['id']}.json", spec)
        saved = state()
        _event(saved, spec["id"], "idea", "нова стратегія", by)
        _write_json(_root() / "state.json", saved)
    write_cards()
    return {"status": "ok", "id": spec["id"], "now": "idea", "next": "action=backtest"}


Fetch = Callable[[str, str, str, int], List[List[Any]]]


def frames(spec: Mapping[str, Any], fetch: Fetch, bars: int = BACKTEST_BARS) -> Dict[str, Any]:
    from src import sam_strategies

    out: Dict[str, Any] = {}
    for account, source, symbol in sam_strategies.instruments_for(spec):
        try:
            out[f"{account}:{source}:{symbol}"] = sam_strategies.frame_of(fetch(source, symbol, spec["timeframe"], bars))
        except Exception as exc:  # noqa: BLE001 - one dead source is named in the report, never guessed
            logger.info("sam_backtest_source_failed", symbol=symbol, error=type(exc).__name__)
            out[f"{account}:{source}:{symbol}"] = None
    return out


def backtest(sid: str, fetch: Fetch, by: str = "sam", promote: bool = True) -> Dict[str, Any]:
    """Run the gate; an idea that passes goes to paper, one that fails is rejected with the reasons."""
    spec = specs().get(sid)
    if spec is None:
        return {"status": "error", "error": "unknown_strategy"}
    result = sam_backtest.report(spec, frames(spec, fetch))
    if result["status"] != "ok":
        return {"id": sid, **result}
    with _LOCK:
        saved = state()
        current = status_of(sid, spec, saved)
        target = current
        if promote and current in ("idea", "rejected"):
            paper_now = sum(1 for k, s in specs().items() if status_of(k, s, saved) == "paper")
            target = ("paper" if paper_now < MAX_PAPER else "idea") if result["passed"] else "rejected"
        elif promote and current == "paper" and not result["passed"]:
            target = "archived"  # it worked once; the fresh data says it no longer does
        why = "бектест пройдено" if result["passed"] else "; ".join(result["reasons"])
        if target == "idea" and result["passed"]:
            why = f"бектест пройдено, але паперових місць немає ({MAX_PAPER})"
        _event(saved, sid, target, why, by, backtest=result)
        _write_json(_root() / "state.json", saved)
    write_cards()
    return {"id": sid, "now": target, **result}


def active(timeframe: Optional[str] = None, exclude: Tuple[str, ...] = ()) -> Dict[str, Dict[str, Any]]:
    saved = state()
    return {k: s for k, s in specs().items() if status_of(k, s, saved) == "paper"
            and (timeframe is None or s.get("timeframe") == timeframe) and s.get("timeframe") not in exclude}


# ── Second Brain ──────────────────────────────────────────────────────────────────────────────


def _vault_folder() -> Optional[Path]:
    from src.obsidian_notes import vault_dir_from_env

    root = vault_dir_from_env()
    return root.joinpath(*CARD_DIR) if root is not None else None


def card(sid: str, spec: Mapping[str, Any], row: Mapping[str, Any]) -> str:
    status = row.get("status") or spec.get("status") or "idea"
    bt = row.get("backtest") or {}
    total = bt.get("out_of_sample_total") or {}
    lines = ["---", f"id: {sid}", f"status: {status}", f"author: {spec.get('author')}",
             f"timeframe: {spec.get('timeframe')}", f"style: {spec.get('style')}", f"parent: {spec.get('parent') or ''}",
             "tags: [сем, стратегія, " + status + "]", "generated: sam_catalog", "---", "",
             f"# {spec.get('title', sid)}", "", f"**Гіпотеза:** {spec.get('hypothesis', '')}", "",
             f"**Джерело:** {spec.get('source', '')}", "", "## Правила", "",
             f"- long: `{spec.get('long') or '—'}`, стоп `{spec.get('stop_long') or '—'}`",
             f"- short: `{spec.get('short') or '—'}`, стоп `{spec.get('stop_short') or '—'}`",
             f"- ризик {spec.get('risk')}, ціль {spec.get('rr', MIN_RR)}R, ринки {', '.join(spec.get('markets', []))}", ""]
    if spec.get("parent"):
        lines += [f"Походить від [[{spec['parent']}]].", ""]
    lines += ["## Останній бектест", ""]
    if bt:
        lines += [f"{bt.get('at', '')[:16]} · {'пройдено' if bt.get('passed') else 'не пройдено'} · поза вибіркою: "
                  f"{total.get('trades')} угод, win {total.get('win_rate')}, PF {total.get('profit_factor')}, "
                  f"очікування {total.get('expectancy_r')}R, найгірша просадка {bt.get('worst_drawdown_pct')}%", ""]
        lines += [f"- причина: {r}" for r in bt.get("reasons", [])]
        lines += ["", "| інструмент | угод | PF | очік. R | дохід % | просадка % | купити й тримати % |",
                  "|---|---|---|---|---|---|---|"]
        for key, res in (bt.get("per_symbol") or {}).items():
            o = res["out_of_sample"]
            lines.append(f"| {key} | {o['trades']} | {o['profit_factor']} | {o['expectancy_r']} | {o['return_pct']} | "
                         f"{o['max_drawdown_pct']} | {o['buy_hold_pct']} |")
    else:
        lines.append("Ще не тестувалася.")
    lines += ["", "## Історія", ""]
    lines += [f"- {h['at'][:16]} {h.get('from') or '—'} → {h['to']} ({h.get('by')}): {h.get('why')}"
              for h in row.get("history", [])] or ["- з репозиторію, без змін"]
    return "\n".join(lines) + "\n"


def write_cards() -> Optional[Path]:
    """Rewrite every card and the index; a card Andrii marked protected is left as it is."""
    from src.obsidian_archivist import is_protected

    folder = _vault_folder()
    if folder is None:
        return None
    try:
        folder.mkdir(parents=True, exist_ok=True)
        saved, every = state(), specs()
        rows = []
        for sid, spec in sorted(every.items()):
            row = saved.get(sid, {})
            path = folder / f"{sid}.md"
            if not (path.is_file() and is_protected(path.read_text(encoding="utf-8", errors="replace"))):
                path.write_text(card(sid, spec, row), encoding="utf-8")
            rows.append((status_of(sid, spec, saved), sid, spec))
        index = ["---", "tags: [сем, стратегії, каталог]", "generated: sam_catalog", "---", "", "# Каталог стратегій Сема", "",
                 f"Оновлено {_now()[:16]} UTC. Статуси: {' → '.join(STATUSES)}.", ""]
        for status in STATUSES:
            chosen = [r for r in rows if r[0] == status]
            if chosen:
                index += [f"## {status} ({len(chosen)})", ""]
                index += [f"- [[{sid}]] — {s.get('title')} · {s.get('timeframe')} · {s.get('author')}" for _, sid, s in chosen]
                index.append("")
        (folder / "Каталог.md").write_text("\n".join(index), encoding="utf-8")
    except OSError as exc:
        logger.warning("sam_catalog_cards_failed", error=type(exc).__name__)
        return None
    return folder


# ── Sam's tool ────────────────────────────────────────────────────────────────────────────────


def _summary(sid: str, spec: Mapping[str, Any], saved: Mapping[str, Any]) -> Dict[str, Any]:
    bt = (saved.get(sid) or {}).get("backtest") or {}
    return {"id": sid, "title": spec.get("title"), "status": status_of(sid, spec, saved), "timeframe": spec.get("timeframe"),
            "author": spec.get("author"), "parent": spec.get("parent"),
            "backtest": {"at": bt.get("at"), "passed": bt.get("passed"), **(bt.get("out_of_sample_total") or {})} if bt else None}


def _list(args: Mapping[str, Any], fetch: Fetch) -> Dict[str, Any]:
    saved = state()
    wanted = args.get("status")
    rows = [_summary(k, s, saved) for k, s in sorted(specs().items()) if not wanted or status_of(k, s, saved) == wanted]
    return {"status": "ok", "strategies": rows, "statuses": list(STATUSES), "paper_slots": MAX_PAPER}


def _get(args: Mapping[str, Any], fetch: Fetch) -> Dict[str, Any]:
    sid = str(args.get("id", ""))
    spec = specs().get(sid)
    if spec is None:
        return {"status": "error", "error": "unknown_strategy"}
    return {"status": "ok", "spec": spec, "state": state().get(sid, {}), "now": status_of(sid, spec)}


def _propose(args: Mapping[str, Any], fetch: Fetch) -> Dict[str, Any]:
    spec = args.get("spec")
    if not isinstance(spec, dict):
        return {"status": "error", "error": "spec_must_be_an_object"}
    made = propose(dict(spec), by="sam")
    if made["status"] == "ok" and args.get("backtest", True):
        return {**made, **backtest(made["id"], fetch)}
    return made


def _backtest(args: Mapping[str, Any], fetch: Fetch) -> Dict[str, Any]:
    return backtest(str(args.get("id", "")), fetch)


def _archive(args: Mapping[str, Any], fetch: Fetch) -> Dict[str, Any]:
    why = str(args.get("why", "")).strip()
    if not why:
        return {"status": "error", "error": "why_is_required"}
    return set_status(str(args.get("id", "")), "archived", why, "sam")


ACTIONS: Dict[str, Callable[[Mapping[str, Any], Fetch], Dict[str, Any]]] = {
    "list": _list, "get": _get, "propose": _propose, "backtest": _backtest, "archive": _archive}


def tool(args: Mapping[str, Any], fetch: Fetch) -> Dict[str, Any]:
    action = args.get("action")
    if action not in ACTIONS:
        return {"status": "error", "error": "unknown_action", "available_actions": sorted(ACTIONS)}
    return ACTIONS[str(action)](args, fetch)
