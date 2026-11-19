"""Build Sam's manual paper journal. Run with Python and openpyxl."""
import argparse
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

LAST = 201
END = 2 * (LAST - 1) + 1
SET = "'Налаштування'!$B$"
DEP, START = SET + "2", SET + "6"
DATE = "dd.mm.yyyy"
TIME = DATE + " hh:mm"
PCT = "0.00%"
NUM = '#,##0.00;[Red](#,##0.00);0.00'
TRADE = ["Тип запису", "Вхід · час", "Ринок", "Інструмент", "Напрямок", "Вхід", "Стоп", "Ціль",
         "Обсяг", "$ за 1 пункт × одиницю", "Ризик $", "Ризик %", "Вихід", "Витрати $",
         "Результат $", "Результат R", "Причина входу", "Хто погодив", "Статус", "Закриття · час", "План R:R", "Перевірка"]
BET = ["Тип запису", "Час ставки", "Подія", "Ринок", "Коефіцієнт", "Імовірність Сема", "EV",
       "Банк до ставки $", "Ставка Келлі $", "Паперова сума $", "Результат", "Закривальний коеф.", "CLV",
       "Результат $", "Результат R", "Розрахунок · час"]
SUMMARY = ["Період", "Початок", "Кінець", "Закрито", "Угод", "Ставок", "Виграшні", "Profit factor",
           "Середнє R", "Підсумок $", "Макс. просадка", "Середній CLV", "Денна межа"]


def choice(ws, col, options):
    rule = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=True)
    rule.showErrorMessage = True
    rule.error = "Обери значення зі списку."
    ws.add_data_validation(rule)
    rule.add(f"{col}2:{col}{LAST}")


def formula(ws, addr, value):
    ws[addr] = "=" + value
    ws[addr].font = Font(color="164E42")


def setup(ws):
    for row in [
        ("Параметр", "Значення"),
        ("Стартовий паперовий депозит, USD", None), ("Ризик на угоду", .01),
        ("Денна межа", -.03), ("Мінімальне R:R", 2.5), ("Перший день місяця обліку", None),
        ("Частка Келлі (0–100%)", None), ("Мінімум закритих угод", None),
        ("Мінімум розрахованих ставок", None), ("Максимальна просадка (додатна частка)", None),
        ("Мінімальний середній CLV", None),
    ]:
        ws.append(row)
    for i in [3, 4, 7, 10, 11]:
        ws[f"B{i}"].number_format = PCT
    ws["B6"].number_format = DATE


def trades(ws):
    ws.append(TRADE)
    for col, values in {"A": ["ПРИКЛАД", "ПАПІР"], "C": ["Форекс", "Крипта", "Акції", "Ф’ючерси"],
                        "E": ["Лонг", "Шорт"], "S": ["План", "Відкрита", "Закрита", "Скасована"]}.items():
        choice(ws, col, values)
    for i in range(2, LAST + 1):
        # f-string expressions use compact cell addresses to keep formulas auditable.
        long = f'AND(E{i}="Лонг",G{i}<F{i},H{i}>F{i})'
        short = f'AND(E{i}="Шорт",G{i}>F{i},H{i}<F{i})'
        valid = f'AND(COUNT(F{i}:J{i})=5,MIN(F{i}:J{i})>0,OR({long},{short}))'
        formula(ws, f"K{i}", f'IF({valid},ABS(F{i}-G{i})*I{i}*J{i},"")')
        formula(ws, f"L{i}", f'IF(AND(ISNUMBER(K{i}),{DEP}>0),K{i}/{DEP},"")')
        settled = f'AND(ISNUMBER(K{i}),S{i}="Закрита",ISNUMBER(B{i}),ISNUMBER(T{i}),T{i}>=B{i},ISNUMBER(M{i}),M{i}>0,ISNUMBER(N{i}),N{i}>=0)'
        formula(ws, f"O{i}", f'IF({settled},IF(E{i}="Лонг",M{i}-F{i},F{i}-M{i})*I{i}*J{i}-N{i},"")')
        formula(ws, f"P{i}", f'IF(ISNUMBER(O{i}),O{i}/K{i},"")')
        formula(ws, f"U{i}", f'IF(ISNUMBER(K{i}),ABS(H{i}-F{i})/ABS(F{i}-G{i}),"")')
        formula(ws, f"V{i}", f'IF(A{i}="","",IF(OR(K{i}="",L{i}="",Q{i}="",R{i}="",C{i}="",D{i}="",B{i}="",S{i}="",AND(S{i}="Закрита",O{i}="")),"Бракує даних",IF(OR(L{i}>{SET}3,U{i}<{SET}5),"Поза межею","У межах")))')
        for col in "BT":
            ws[f"{col}{i}"].number_format = TIME
        ws[f"L{i}"].number_format = PCT


def bets(ws):
    ws.append(BET)
    choice(ws, "A", ["ПРИКЛАД", "ПАПІР"])
    choice(ws, "K", ["Відкрита", "Виграш", "Програш", "Повернення", "Скасована"])
    for i in range(2, LAST + 1):
        valid = f'AND(E{i}>1,ISNUMBER(F{i}),F{i}>=0,F{i}<=1)'
        formula(ws, f"G{i}", f'IF({valid},E{i}*F{i}-1,"")')
        formula(ws, f"I{i}", f'IF(AND(ISNUMBER(G{i}),H{i}>0,ISNUMBER({SET}7),{SET}7>=0,{SET}7<=1),ROUND(MAX(0,G{i}/(E{i}-1))*{SET}7*H{i},2),"")')
        formula(ws, f"M{i}", f'IF(AND(E{i}>1,L{i}>1),E{i}/L{i}-1,"")')
        valid_result = f'AND(ISNUMBER(B{i}),ISNUMBER(P{i}),P{i}>=B{i},E{i}>1,J{i}>0)'
        formula(ws, f"N{i}", f'IF({valid_result},IF(K{i}="Виграш",J{i}*(E{i}-1),IF(K{i}="Програш",-J{i},IF(K{i}="Повернення",0,""))),"")')
        formula(ws, f"O{i}", f'IF(ISNUMBER(N{i}),N{i}/J{i},"")')
        for col in "BP":
            ws[f"{col}{i}"].number_format = TIME
        for col in "FGM":
            ws[f"{col}{i}"].number_format = PCT


def examples(trade, bet):
    day = datetime(2026, 1, 12, 10)
    close = datetime(2026, 1, 12, 15)
    rows = [
        (trade, 2, dict(A="ПРИКЛАД", B=day, C="Акції", D="Демо А", E="Лонг", F=50, G=48, H=55, I=1, J=1,
                        M=54, N=0, Q="Демонстрація розрахунку", R="Умовний оператор", S="Закрита", T=close)),
        (trade, 3, dict(A="ПРИКЛАД", B=day, C="Ф’ючерси", D="Демо Б", E="Шорт", F=100, G=102, H=94,
                        I=1, J=5, Q="Приклад множника", R="Умовний оператор", S="План")),
        (bet, 2, dict(A="ПРИКЛАД", B=day, C="Умовний матч", D="Перемога А", E=2.1, F=.50, H=100,
                      J=1, K="Програш", L=2.0, P=close)),
    ]
    for ws, i, fields in rows:
        for col, value in fields.items():
            ws[f"{col}{i}"] = value


def ledger(ws):
    # Source rows P:U, chronological realized-equity ledger V:AC.
    for idx in range(2, END + 1):
        trade = idx <= LAST
        row = idx if trade else idx - LAST + 1
        name = "'Угоди'!" if trade else "'Ставки'!"
        pnl, r_mult, timestamp = ("O", "P", "T") if trade else ("N", "O", "P")
        t = f"{name}{timestamp}{row}"
        p = f"{name}{pnl}{row}"
        valid = f'AND({name}A{row}="ПАПІР",ISNUMBER({p}),ISNUMBER({START}),{t}>={START},{t}<EDATE({START},1))'
        formula(ws, f"P{idx}", f'IF({valid},{t},"")')
        for col, value in [("Q",p), ("R",f"{name}{r_mult}{row}"), ("S",'"Угода"' if trade else '"Ставка"')]:
            formula(ws, f"{col}{idx}", f'IF(ISNUMBER(P{idx}),{value},"")')
        if not trade:
            clv = f"{name}M{row}"
            formula(ws, f"T{idx}", f'IF(AND(ISNUMBER(P{idx}),ISNUMBER({clv})),{clv},"")')
        formula(ws, f"U{idx}", f'IF(ISNUMBER(P{idx}),COUNTIF(P$2:P${END},"<"&P{idx})+COUNTIF(P$2:P{idx},P{idx}),"")')
        formula(ws, f"V{idx}", f'IFERROR(MATCH(ROW()-1,U$2:U${END},0),"")')
        for dst, src in [("W","P"), ("X","Q")]:
            formula(ws, f"{dst}{idx}", f'IF(ISNUMBER(V{idx}),INDEX({src}$2:{src}${END},V{idx}),"")')
        formula(ws, f"Y{idx}", f'IF(AND(ISNUMBER(X{idx}),{DEP}>0),{DEP}+SUM(X$2:X{idx}),"")')
        formula(ws, f"Z{idx}", f'IF(ISNUMBER(Y{idx}),MAX({DEP},Y$2:Y{idx}),"")')
        formula(ws, f"AA{idx}", f'IF(ISNUMBER(Y{idx}),1-Y{idx}/Z{idx},"")')
    for col in range(16, 28):
        ws.column_dimensions[get_column_letter(col)].hidden = True


def summary(ws):
    ws.append(SUMMARY)
    ledger(ws)
    for i in range(2, 39):
        daily = i <= 32
        weekly = 33 <= i <= 37
        offset = i-2 if daily else (i-33)*7 if weekly else 0
        span = 1 if daily else 7 if weekly else 32
        ws[f"A{i}"] = "День" if daily else "Тиждень" if weekly else "Місяць"
        formula(ws, f"B{i}", f'IF(AND(ISNUMBER({START}),{START}+{offset}<EDATE({START},1)),{START}+{offset},"")')
        formula(ws, f"C{i}", f'IF(ISNUMBER(B{i}),MIN(B{i}+{span}-1,EDATE({START},1)-1),"")')
        lo, hi = f'">="&B{i}', f'"<"&(C{i}+1)'
        period = f'P$2:P${END},{lo},P$2:P${END},{hi}'
        def put(col, expression, row=i):
            formula(ws, f"{col}{row}", f'IF(ISNUMBER(B{row}),{expression},"")')
        put("D", f'COUNTIFS({period})')
        for col, kind in [("E","Угода"),("F","Ставка")]:
            put(col, f'COUNTIFS({period},S$2:S${END},"{kind}")')
        put("G", f'IFERROR(COUNTIFS({period},Q$2:Q${END},">0")/D{i},"")')
        put("H", f'IFERROR(-SUMIFS(Q$2:Q${END},{period},Q$2:Q${END},">0")/SUMIFS(Q$2:Q${END},{period},Q$2:Q${END},"<0"),"")')
        put("I", f'IFERROR(AVERAGEIFS(R$2:R${END},{period}),"")')
        put("J", f'IF(D{i}>0,SUMIFS(Q$2:Q${END},{period}),"")')
        first = f'1+COUNTIFS(W$2:W${END},">0",W$2:W${END},"<"&B{i})'
        data = f'AA$2:AA${END}'
        put("K", f'IF(AND(D{i}>0,{DEP}>0),MAX(INDEX({data},{first}):INDEX({data},{first}+D{i}-1)),"")')
        put("L", f'IFERROR(AVERAGEIFS(T$2:T${END},{period},S$2:S${END},"Ставка"),"")')
        if daily:
            opening = f'({DEP}+SUM(J$1:J{i-1}))'
            put("M", f'IF(AND(D{i}>0,{DEP}>0,{opening}>0),IF(J{i}/{opening}<={SET}4,"Досягнуто","У межах"),"")')
        for col in "BC":
            ws[f"{col}{i}"].number_format = DATE
        for col in "GKL":
            ws[f"{col}{i}"].number_format = PCT
    ws["A40"] = "Прохід місяця"
    formula(ws, "B40", f'IF(OR(COUNT({SET}8:{SET}11)<4,{DEP}<=0,COUNT({START})=0),"Заповни налаштування",IF(TODAY()<EDATE({START},1),"Місяць триває",IF(D38=0,"Немає даних",IF(AND(E38>={SET}8,F38>={SET}9,ISNUMBER(K38),K38<={SET}10,ISNUMBER(L38),L38>={SET}11),"Пройдено","Не пройдено"))))')
    for word, color in [("Пройдено","B7E4C7"),("Не пройдено","FFC7CE")]:
        ws.conditional_formatting.add("B40", CellIsRule(operator="equal", formula=[f'"{word}"'],
                                     fill=PatternFill("solid", fgColor=color)))


def guide(ws):
    rows = [
        ("Поле / дія", "Як заповнювати й читати"),
        ("Початок", "У Налаштуваннях введи депозит у USD, дату старту, частку Келлі й критерії. Книга розрахована на один місяць від дати старту і 200 рядків кожного журналу разом із прикладами."),
        ("Тип запису", "Обирай ПАПІР. Три рядки ПРИКЛАД виключено з усіх підсумків. Для нової операції використовуй порожній рядок."),
        ("Час", "Вводь дату й час за Києвом. Підсумки беруть дату закриття угоди або розрахунку ставки. Однакові моменти впорядковуються за рядком, спочатку угоди."),
        ("Ринок, інструмент, напрямок", "Обери клас активу, запиши символ та лонг або шорт. Вхід, стоп, ціль і вихід — ціни в одній шкалі."),
        ("Обсяг і множник", "Обсяг — кількість одиниць або контрактів. Множник — доларова зміна вартості одиниці при зміні ціни на 1. Для USD-акції це 1. Для іншої валюти врахуй конвертацію у USD."),
        ("Ризик і R:R", "Ризик $ = відстань до стопа × обсяг × множник. Ризик % від початкового депозиту. Планове R:R = відстань до цілі / відстань до стопа. Стоп і ціль перевіряються за напрямком."),
        ("Статус, причина, погодження", "Запиши аргумент входу та ім’я того, хто погодив. Перевірка позначає неповний запис або перевищення порогу. Для закриття потрібні вихід, час і витрати; якщо витрат немає, введи 0."),
        ("Результат угоди", "Різниця цін з урахуванням напрямку × обсяг × множник мінус витрати. R = чистий результат / початковий ризик у доларах."),
        ("Подія, ринок, коефіцієнти", "Запиши матч чи подію, тип ринку, десяткові коефіцієнти відкриття і закриття того самого вибору та ринку. Імовірність вводь у відсотках."),
        ("EV, банк і Келлі", "EV = імовірність × коефіцієнт − 1. Рекомендована паперова сума = банк перед ставкою × частка Келлі × max(0, EV / (коефіцієнт − 1)). Фактичну паперову суму введи окремо."),
        ("Результат ставки, CLV", "Виграш дає сума × (коефіцієнт − 1), програш дає мінус суму, повернення дає 0. R дорівнює результату, поділеному на суму. CLV = початковий коефіцієнт / закривальний − 1."),
        ("Дні, тижні, місяць", "Тижні — семиденні відрізки від початку обліку. В підсумки входять розраховані паперові записи обох журналів. Відкриті та скасовані не рахуються. Повернення входить у знаменник відсотка виграшів."),
        ("Profit factor, очікування, CLV", "Profit factor = сума прибутків / абсолютну суму збитків; без збитків поле порожнє. Очікування — середнє R на запис. Середній CLV враховує лише ставки з обома коефіцієнтами."),
        ("Просадка й денна межа", "Просадка після кожного розрахунку = 1 − поточний капітал / попередній максимум від початку місяця включно з депозитом. У періоді показано найбільшу таку просадку. Денна межа зіставляє чистий підсумок дня з капіталом на початку дня; відкриті збитки не оцінюються."),
        ("Прохід", "Усі чотири критерії заповнює Андрій. Після завершення місяця перевіряються мінімальні кількості угод і ставок, максимальна просадка й мінімальний середній CLV. Без даних про CLV критерій не пройдено. Це оцінка паперової роботи."),
    ]
    for row in rows:
        ws.append(row)


def build(path):
    wb = Workbook()
    settings = wb.active
    settings.title = "Налаштування"
    trade, bet, totals, help_sheet = [wb.create_sheet(s) for s in ("Угоди","Ставки","Підсумки","Довідка")]
    setup(settings)
    trades(trade)
    bets(bet)
    examples(trade, bet)
    summary(totals)
    guide(help_sheet)
    for ws in wb:
        ws.freeze_panes = "C2" if ws in (trade, bet) else "A2"
        ws.sheet_view.showGridLines = False
        for cell in ws[1]:
            if cell.value is None:
                continue
            cell.font = Font(color="FFFFFF", bold=True)
            cell.fill = PatternFill("solid", fgColor="194B50")
            ws.column_dimensions[cell.column_letter].width = max(15, len(cell.value) + 4)
        ws.row_dimensions[1].height = 28
    for ws in (trade, bet):
        ws.auto_filter.ref = ws.dimensions
    settings.column_dimensions["A"].width = 49
    settings.column_dimensions["B"].width = 23
    totals.column_dimensions["B"].width = 28
    help_sheet.column_dimensions["A"].width = 32
    help_sheet.column_dimensions["B"].width = 98
    for row in list(help_sheet.rows)[1:]:
        row[1].alignment = Alignment(wrap_text=True, vertical="center")
        help_sheet.row_dimensions[row[1].row].height = 50
    wb.save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--legacy", action="store_true", help="Build the original five-sheet workbook.")
    args = parser.parse_args()
    if args.legacy:
        build(args.output)
    else:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from tools.sam_sheet.desks import build as build_desks
        build_desks(args.output)
