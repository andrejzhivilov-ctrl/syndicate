"""What must not be spoken aloud or kept in chat memory (operator decision 29.10).

Three things only:

* operational military information: a coordinate pair, or a unit word together
  with an operational detail ("бригада ... стоїть під ...", "рота переміщується").
  News-like mentions ("ЗСУ звільнили село") are not operational and pass;
* account numbers: Ukrainian IBAN, payment cards (Luhn-checked), "рахунок № ...";
* passwords and access codes.

Everything else may be voiced as is. Detection is deterministic regex, so it adds
no latency: a local model on this server took 10-20 s per check (benchmark 28.10).
"""
from __future__ import annotations

import re
from typing import List, Tuple

from src.agents.eva_memory_policy import EvaMemoryPolicy

_COORDINATES = re.compile(r"(?<!\d)[+-]?\d{1,2}[.,]\d{3,}\s*[,;/ ]\s*[+-]?\d{1,3}[.,]\d{3,}(?!\d)")
_MGRS = re.compile(r"\b\d{1,2}[C-HJ-NP-X]\s?[A-HJ-NP-Z]{2}\s?\d{4,5}\s?\d{4,5}\b")
_FORCE = re.compile(
    r"(?i)\b(?:бригад\w*|батальйон\w*|рот[аиуоі]|взвод\w*|підрозділ\w*|полк\w*|дивізіон\w*|"
    r"окбр|омбр|ошб|одшбр|тро|дшв|сзч|екіпаж\w*|розрахун[ок]\w*\s+(?:дрон|бпла|ппо|міномет)\w*|"
    r"бпла|дрон\w*|mavic|ребів|реб|ппо|гаубиц\w*|міномет\w*|танк\w*|бмп|бтр|himars|"
    r"brigade|battalion|platoon)\b"
)
_OPERATIONAL = re.compile(
    r"(?i)\b(?:позиці\w*|переміщ\w*|перемісти\w*|висува\w*|висунут\w*|стоять|стоїть|стоїмо|"
    r"розташ\w*|дислок\w*|ротаці\w*|заход\w*\s+на|виход\w*\s+з|штурм\w*|координат\w*|маршрут\w*|"
    r"бліндаж\w*|окоп\w*|опорн\w*\s+пункт\w*|вогнев\w*|склад\w*\s+(?:бк|боєприпас\w*)|боєкомплект\w*|"
    r"кількіст\w*\s+(?:особового|людей|бійців|техніки)|особов\w*\s+склад\w*|"
    r"position\w*|deploy\w*|moving|redeploy\w*|coordinates)\b"
)
_IBAN = re.compile(r"\bUA\d{2}\s?(?:[A-Z0-9]\s?){25}\b")
_CARD = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
_ACCOUNT = re.compile(r"(?i)\b(?:рахун\w*|account)\s*(?:№|номер|no\.?|#)?\s*[:№]?\s*\d[\d -]{7,}\d")
_ACCESS_CODE = re.compile(
    r"(?i)\b(?:парол\w*|password|passcode|pin(?:-код)?|пін(?:-код)?|cvv|cvc|otp|2fa|"
    r"код\w*\s+(?:доступу|підтвердження|входу|з\s+смс|із\s+смс)|одноразов\w*\s+код\w*|seed[- ]?фраз\w*)"
    r"\s*(?:[:=—–-]|це|is)?\s*\S{3,}"
)

VOICE_NOTICE = "Ця відповідь містить чутливі дані, тому лише текстом."


def is_military(text: str) -> bool:
    """Operational military detail, not a mere mention of the war or the army."""
    if not isinstance(text, str) or not text:
        return False
    if _COORDINATES.search(text) or _MGRS.search(text):
        return True
    return bool(_FORCE.search(text) and _OPERATIONAL.search(text))


def _luhn(digits: str) -> bool:
    total, parity = 0, len(digits) % 2
    for i, ch in enumerate(digits):
        d = int(ch)
        if i % 2 == parity:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0


def _card(match: "re.Match[str]") -> str:
    digits = re.sub(r"\D", "", match.group(0))
    return "номер картки — у тексті" if 13 <= len(digits) <= 19 and _luhn(digits) else match.group(0)


_SPOKEN_MASKS = (
    (_IBAN, lambda m: "номер рахунку — у тексті"),
    (_ACCOUNT, lambda m: "номер рахунку — у тексті"),
    (_CARD, _card),
    (_ACCESS_CODE, lambda m: "код доступу — у тексті"),
)


def mask_for_voice(text: str) -> Tuple[str, List[str]]:
    """Replace account numbers and access codes with a spoken pointer to the text."""
    kinds: List[str] = []
    for pattern, replace in _SPOKEN_MASKS:
        def sub(match: "re.Match[str]", _replace=replace) -> str:
            spoken = _replace(match)
            if spoken != match.group(0):
                kinds.append(spoken.split(" —")[0])
            return spoken
        text = pattern.sub(sub, text)
    return text, kinds


def voice_text(heard: str, reply: str) -> Tuple[str, str]:
    """(what to voice, why). Military talk is never voiced; numbers and codes are masked."""
    if is_military(heard) or is_military(reply):
        return VOICE_NOTICE, "military"
    if EvaMemoryPolicy.contains_secret_like_value(reply):
        return VOICE_NOTICE, "secret"
    spoken, kinds = mask_for_voice(reply)
    return spoken, ("masked" if kinds else "plain")
