"""Air-raid notifications from the operator's own phrase bank (29.10), never the same twice in a row.

alerts.in.ua ``/v2/iot/active_air_raid_alerts/{uid}.json`` returns one character per
location: ``R`` red (direct danger), ``Y`` yellow (preliminary threat), ``P`` alert in
part of the region, ``N`` no alert. ``AlertTracker.update`` turns every change of level
(alert, yellow↔red, all-clear) into one phrase; the all-clear depends on the highest
level seen during the alert.
Anything else (an unknown character, a missing reading) gives no message: the bot never
announces an alert or an all-clear it did not observe.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence

YELLOW: Sequence[str] = (
    "Ваньки на болотах заворушилися. Поки що просто чухаються, але вуха тримаємо гостро.",
    "У півнів загострення: запустили свої бляшанки. Не панікуємо, але маршрут до безпечного місця згадуємо.",
    "Жовтий рівень: болотяні півні злетіли покататися. Заряджаємо павербанки й придивляємося до двох стін.",
    "Шось ванька смикає за важелі. Ситуація під контролем, але чайок краще допивати ближче до коридору.",
    "Увага, півнячий двіж на горизонті. Без істерик, просто не будьте легковажними.",
    "Болотяна авіація вирішила полякати ворон. Стежимо за рухом, але борщ варити не припиняємо.",
    "Півні завели свої мопеди. Дзижчать десь далеко, але капці біля ліжка краще поставити зручно.",
    "Ванька натиснув якусь кнопку й сам злякався. Ситуація під наглядом, зайвий раз у вікно не визираємо.",
    "У курнику суєта: злетіли борти. Поки що летять суто повимахуватися, але зарядки до телефонів тримайте ближче.",
    "Жовтий. Півнячий стендап починається, запасаємося терпінням і водою.",
)

RED: Sequence[str] = (
    "Червоний! Ваньки пустили свій металобрухт. Швидко за дві стіни або в укриття, вікна самі себе не заклеять!",
    "Півні закукурікали ракетами. Всі в безпечні місця! Дозволяється матюкатися, забороняється стояти біля вікна.",
    "Летять подарунки від кончених. Не випробовуйте долю, ванька цілиться абияк, тож ноги в руки — і в сховище!",
    "Повна тривога! На болотах знову прорвало каналізацію. Ховаємося, поки хлопці мінусують цю нечисть.",
    "Півнячий десант у повітрі. Ніяких зйомок ППО, тільки коридор, ванна чи підвал. Бережемо себе!",
    "Ванька пустив дурне! Всім у безпечні кутки, балкон почекає, життя дорожче!",
    "Півні геть подуріли, летить залізяччя. Бігом за дві стіни, зараз буде гучно працювати наша арта й ППО!",
    "Червоний! У ваньки критичні дні — шпурляє чим попало. Падаємо на підлогу або в коридор, бережемо голови!",
    "Півнячий експрес на підльоті. Не будьте героями для соцмереж: телефон у кишеню, дупу в безпечне місце.",
    "Увага, кончені активізувалися на максимум! Вікна геть, штори закрити, зуби стиснути й чекати роботи козаків.",
)

#: After a red alert: everything was shot down.
CLEAR_AFTER_RED: Sequence[str] = (
    "Відбій! Усі півні збиті або пішли на дно. Можна вилазити з коридорів і ставити чайник.",
    "Ваньки отримали по зубах, небо чисте. Дякуємо силам ППО, повертаємося до справ!",
    "Болотяні півники відкукурікали своє. Відбій, видихаємо, але донатити не забуваємо.",
    "Ваньчин металобрухт успішно розібрано на добрива. Всім спокійного дня/ночі, небезпека минула.",
    "Відбій! Півні полягали спати (деякі — назавжди). Виходимо на світло боже.",
    "Півнячий цирк поїхав, клоуни збиті. Відбій, повертаємося до нормального життя!",
    "Ваньки підтерли соплі й пішли курить бамбук. Небо чисте, ППО — боги, козаки — кращі.",
    "Усі літаючі балалайки пішли на дрова. Відбій тривоги, можна розгинати спини й ставити вечерю.",
    "Півні втомилися отримувати по дзьобу й вгамувалися. Вилазимо зі схованок, але пильність не втрачаємо.",
    "Чисто! Металобрухт утилізовано, ванька плаче в кутку. Дякуємо силам оборони та видихаємо!",
)

#: After only a yellow alert: calm down and disperse (operator, 29.10).
CLEAR_AFTER_YELLOW: Sequence[str] = (
    "Відбій жовтого. Все спокійно, розходимося.",
    "Півні покрутилися й передумали. Відбій, все спокійно — розходимося по справах.",
    "Ваньки почухалися й заспокоїлися. Відбій, можна видихнути й розходитися.",
    "Жовтий знято. Болотяна авіація повернулася в курник, все спокійно, розходимося.",
    "Відбій: двіж на болотах стих. Капці можна відсунути, все спокійно.",
)

#: Yellow escalated to red during the same alert.
ESCALATE_TO_RED: Sequence[str] = (
    "Жовтий переріс у червоний! Ваньки перейшли від чухання до запусків — бігом за дві стіни.",
    "Півні дочухалися й таки пустили залізяччя. Червоний рівень, всі в укриття!",
    "Підвищуємо ставки: було жовто, стало червоно. Чайок лишаємо, самі — в коридор.",
    "Болотяна авіація перейшла в атаку. Червоний! Від вікон геть, телефон у кишеню.",
    "Ванька таки натиснув червону кнопку. Без героїзму: укриття, ванна чи підвал.",
    "Двіж на болотах переріс у концерт. Червоний рівень — ховаємося, поки ППО працює.",
    "Мопеди півнів звернули в наш бік. Червоний! Ноги в руки й у безпечне місце.",
    "Жовта увага закінчилась — почалась червона небезпека. Дві стіни, і без зйомок неба.",
    "Курник остаточно сказився: летить усе, що не прибито. Червоний, бережемо голови!",
    "Стендап півнів перейшов у трагедію для них, але нам ризикувати не можна. Червоний — в укриття!",
    "Кончені розійшлися не на жарт. Рівень червоний, балкон почекає.",
    "Ванька прицілився абияк, а значить, куди завгодно. Червоний! Швидко в коридор.",
)

#: Red eased to yellow: the direct danger passed, the alert is not over yet.
EASE_TO_YELLOW: Sequence[str] = (
    "Червоний знято, лишається жовтий. Найгучніше позаду, але з укриття не вистрибуємо стрімголов.",
    "Першу хвилю півнів розібрали. Рівень знизився до жовтого — видихаємо наполовину.",
    "Металобрухт у повітрі закінчився, але ваньки ще ворушаться. Жовтий, тримаємо вуха гостро.",
    "Червоне відкукурікали, далі жовте. Можна виглянути з коридору, але чайник поки не ставимо.",
    "Головну партію збили, тепер жовтий. ППО молодці, ми — ще трохи обережні.",
    "Півні видихлися, але не всі. Знижуємося до жовтого, зарядки ще тримаємо під рукою.",
    "Залізяччя більше не летить у наш бік. Жовтий рівень — без паніки, але й без легковажності.",
    "Ванька перезаряджається, а ми переводимо подих. Жовтий, стежимо далі.",
    "Червоний минув. Лишається жовтий шум на болотах — пильність не вимикаємо.",
    "Козаки відпрацювали, загроза знизилась до жовтої. Сидимо ближче до двох стін ще трохи.",
    "Курник притих, але не заснув. Жовтий рівень — вікна ще обходимо.",
    "Найгірше позаду, жовтий лишається. Дочекаємося повного відбою — і тоді вже дрихнути.",
)

PARTIAL_NOTE = "(тривога лише в частині регіону)"
_LEVEL = {"R": 2, "Y": 1, "P": 1, "N": 0}


class PhraseBag:
    """Every phrase of a pool once before any repeats; never the same phrase twice in a row."""

    def __init__(self, pools: Dict[str, Sequence[str]], rng: Optional[random.Random] = None) -> None:
        self._pools = pools
        self._rng = rng or random.Random()
        self._left: Dict[str, List[str]] = {}
        self._last: Dict[str, str] = {}

    def draw(self, pool: str) -> str:
        if not self._left.get(pool):
            fresh = list(self._pools[pool])
            self._rng.shuffle(fresh)
            if len(fresh) > 1 and fresh[-1] == self._last.get(pool):
                fresh[0], fresh[-1] = fresh[-1], fresh[0]
            self._left[pool] = fresh
        phrase = self._left[pool].pop()
        self._last[pool] = phrase
        return phrase


POOLS: Dict[str, Sequence[str]] = {
    "yellow": YELLOW, "red": RED, "escalate_to_red": ESCALATE_TO_RED, "ease_to_yellow": EASE_TO_YELLOW,
    "clear_after_red": CLEAR_AFTER_RED, "clear_after_yellow": CLEAR_AFTER_YELLOW,
}
DEFAULT_BAG = PhraseBag(POOLS)


class AlertTracker:
    """Turns successive alerts.in.ua status characters into notifications."""

    def __init__(self, bag: PhraseBag = DEFAULT_BAG) -> None:
        self._bag = bag
        self._current: Optional[str] = None
        self._peak = 0

    def update(self, status: Optional[str]) -> Optional[str]:
        status = (status or "").strip().upper()
        if status not in _LEVEL:
            return None  # unknown or missing reading: say nothing rather than guess
        previous, self._current = self._current, status
        if previous is None:
            self._peak = _LEVEL[status]
            return None  # first reading after a restart only sets the baseline
        level = _LEVEL[status]
        if level == _LEVEL[previous]:
            return None  # same level (Y and P included): no repeated alarm
        if level == 0:
            peak, self._peak = self._peak, 0
            if not peak:
                return None
            return "🟢 " + self._bag.draw("clear_after_red" if peak == 2 else "clear_after_yellow")
        if level == 2:
            self._peak = 2
            # Every level change is announced (operator, 29.10): yellow → red has its own phrases.
            return "🔴 " + self._bag.draw("escalate_to_red" if _LEVEL[previous] == 1 else "red")
        self._peak = max(self._peak, 1)
        pool = "ease_to_yellow" if previous == "R" else "yellow"
        text = "🟡 " + self._bag.draw(pool)
        return f"{text} {PARTIAL_NOTE}" if status == "P" else text
