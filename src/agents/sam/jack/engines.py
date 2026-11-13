"""Explicit mathematical estimates from supplied inputs, not trained forecasts."""
from __future__ import annotations

import math
from functools import lru_cache

from scipy.stats import norm, poisson

from src.agents.director_base import number


def football(payload: dict) -> dict:
    home = number(payload["home_xg"], "home_xg", 0.001, 10)
    away = number(payload["away_xg"], "away_xg", 0.001, 10)
    rho = number(payload["rho"], "rho", -1, 1)
    limit = int(max(poisson.ppf(1 - 1e-12, home), poisson.ppf(1 - 1e-12, away)))
    matrix = []
    for h in range(limit + 1):
        for a in range(limit + 1):
            correction = {(0, 0): 1 - home * away * rho, (0, 1): 1 + home * rho,
                          (1, 0): 1 + away * rho, (1, 1): 1 - rho}.get((h, a), 1)
            if correction < 0:
                raise ValueError("invalid_dixon_coles_correction")
            matrix.append((h, a, float(poisson.pmf(h, home) * poisson.pmf(a, away) * correction)))
    mass = sum(p for _, _, p in matrix)
    line = number(payload["total_line"], "total_line", 0, 30)
    return {"model": "poisson_dixon_coles", "home_win": sum(p for h, a, p in matrix if h > a) / mass,
            "draw": sum(p for h, a, p in matrix if h == a) / mass,
            "away_win": sum(p for h, a, p in matrix if h < a) / mass,
            "under": sum(p for h, a, p in matrix if h + a < line) / mass,
            "push": sum(p for h, a, p in matrix if h + a == line) / mass,
            "over": sum(p for h, a, p in matrix if h + a > line) / mass,
            "captured_probability_mass": mass}


def basketball(payload: dict) -> dict:
    possessions = number(payload["possessions"], "possessions", 1, 200)
    home_rating = number(payload["home_points_per_100"], "home_points_per_100", 1, 200)
    away_rating = number(payload["away_points_per_100"], "away_points_per_100", 1, 200)
    sigma = number(payload["total_sigma"], "total_sigma", 0.01, 100)
    line = number(payload["total_line"], "total_line", 0, 500)
    expected = possessions * (home_rating + away_rating) / 100
    under = float(norm.cdf(line, loc=expected, scale=sigma))
    return {"model": "possession_normal_baseline", "expected_total": expected,
            "under": under, "over": 1 - under, "calibration": "supplied_ratings_and_sigma"}


def hold_probability(point_win: float) -> float:
    p = number(point_win, "serve_point_probability", 0, 1)
    q = 1 - p
    before_deuce = p ** 4 * (1 + 4 * q + 10 * q ** 2)
    reach_deuce = 20 * p ** 3 * q ** 3
    return before_deuce + reach_deuce * p ** 2 / (p ** 2 + q ** 2)


def tennis(payload: dict) -> dict:
    hold_a = hold_probability(payload["a_serve_point_win"])
    hold_b = hold_probability(payload["b_serve_point_win"])
    tiebreak = number(payload["a_tiebreak_win"], "a_tiebreak_win", 0, 1)
    first = payload["first_server"]
    if first not in {"a", "b"}:
        raise ValueError("invalid_first_server")

    @lru_cache(None)
    def set_win(a: int, b: int) -> float:
        if max(a, b) >= 6 and abs(a - b) >= 2:
            return float(a > b)
        if a == b == 6:
            return tiebreak
        a_serves = ((a + b) % 2 == 0) == (first == "a")
        win = hold_a if a_serves else 1 - hold_b
        return win * set_win(a + 1, b) + (1 - win) * set_win(a, b + 1)

    return {"model": "iid_point_markov_set", "a_hold": hold_a, "b_hold": hold_b,
            "a_set_win": set_win(0, 0), "warning": "Set estimate only; no live fitness or surface adjustment inferred"}


def esports(payload: dict) -> dict:
    discipline = payload["discipline"]
    if discipline not in {"cs2", "dota2", "lol", "valorant"}:
        raise ValueError("unsupported_discipline")
    probabilities = payload["map_win_probabilities"]
    if not isinstance(probabilities, list) or len(probabilities) not in {1, 3, 5, 7}:
        raise ValueError("odd_length_series_required")
    probabilities = [number(p, "map_probability", 0, 1) for p in probabilities]
    distribution = [1.0]
    for p in probabilities:
        updated = [0.0] * (len(distribution) + 1)
        for wins, mass in enumerate(distribution):
            updated[wins] += mass * (1 - p)
            updated[wins + 1] += mass * p
        distribution = updated
    return {"model": "independent_map_exact", "discipline": discipline,
            "series_win": sum(distribution[len(probabilities) // 2 + 1:]),
            "warning": "Conditional on supplied map probabilities; correlated maps are not modeled"}


def poker(payload: dict) -> dict:
    pot = number(payload["pot"], "pot", 0, 1e9)
    call = number(payload["call"], "call", 0.01, 1e9)
    equity = number(payload["equity"], "equity", 0, 1)
    fold_equity = number(payload["fold_equity"], "fold_equity", 0, 1)
    if pot + call <= 0:
        raise ValueError("invalid_pot")
    call_ev = equity * pot - (1 - equity) * call
    risk = number(payload["shove_risk"], "shove_risk", 0.01, 1e9)
    opponent_call = number(payload["opponent_call"], "opponent_call", 0, 1e9)
    called_shove_ev = equity * (pot + opponent_call) - (1 - equity) * risk
    return {"model": "supplied_equity_chip_ev", "break_even_equity": call / (pot + call),
            "call_ev": call_ev, "shove_ev": fold_equity * pot + (1 - fold_equity) * called_shove_ev,
            "warning": "pot is current pot; opponent_call and shove_risk are incremental chips; no GTO ranges inferred"}


def icm(payload: dict) -> dict:
    stacks = tuple(number(s, "stack", 0.01, 1e12) for s in payload["stacks"])
    prizes = tuple(number(p, "prize", 0, 1e12) for p in payload["prizes"])
    if not 2 <= len(stacks) <= 9 or not 1 <= len(prizes) <= len(stacks):
        raise ValueError("icm_field_size")
    if any(a < b for a, b in zip(prizes, prizes[1:], strict=False)):
        raise ValueError("prizes_must_descend")

    @lru_cache(None)
    def solve(remaining: tuple[int, ...], place: int) -> tuple[float, ...]:
        values = [0.0] * len(stacks)
        if place >= len(prizes):
            return tuple(values)
        total = math.fsum(stacks[i] for i in remaining)
        for winner in remaining:
            chance = stacks[winner] / total
            values[winner] += chance * prizes[place]
            rest = solve(tuple(i for i in remaining if i != winner), place + 1)
            for i, value in enumerate(rest):
                values[i] += chance * value
        return tuple(values)

    return {"model": "independent_chip_model", "equities": solve(tuple(range(len(stacks))), 0)}


ENGINES = {"football": football, "basketball": basketball, "tennis": tennis,
           "esports": esports, "poker": poker, "icm": icm}
