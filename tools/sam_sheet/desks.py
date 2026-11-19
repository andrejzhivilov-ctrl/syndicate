"""Build the multi-desk paper workbook with openpyxl."""
from pathlib import Path


from openpyxl import Workbook
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as letter
from openpyxl.worksheet.datavalidation import DataValidation

from . import build as core

DESKS = (("Форекс", "USD", 100), ("Інвестиції", "UAH", 3000),
         ("Крипта", "USD", 100), ("Ставки", "UAH", 1000))
MODES = ["Скальпінг", "Денна", "Середній строк", "Довгий строк", "Новини"]
SPORTS = ["Футбол", "Теніс", "Баскетбол", "Кіберспорт", "Покер"]
LAST = core.LAST
START = "'Налаштування'!$B$6"


def options(ws, col, values):
    core.choice(ws, col, values)


def header(ws, names):
    for i, value in enumerate(names, 1):
        ws.cell(1, i, value)


def style(ws, color="18454F"):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "C2"
    ws.row_dimensions[1].height = 34
    for cell in ws[1]:
        if cell.value is None:
            continue
        cell.font = Font(name="Calibri", bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=color)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[cell.column_letter].width = min(43, max(17, len(str(cell.value))+3))


def configure(ws):
    core.setup(ws)
    ws["A2"] = "Банки напрямів наведено праворуч"
    ws["A6"] = "Дата старту паперового обліку"
    ws["A8"] = "Мінімум угод на напрям"
    ws["A9"] = "Мінімум розрахованих ставок"
    ws["A12"] = "Максимальне плече"
    ws["B12"] = 10
    ws["A13"] = "Перша оцінка, днів"
    ws["B13"] = 14
    ws["A14"] = "Друга оцінка, днів"
    ws["B14"] = 21
    for k, h in enumerate(["Напрям", "Валюта", "Початковий банк"], 4):
        ws.cell(1, k, h)
    for row, desk in enumerate(DESKS, 2):
        for col, value in enumerate(desk, 4):
            ws.cell(row, col, value)
    style(ws)
    ws.column_dimensions["A"].width = 48


def currency_headers(ws, unit):
    for c in ws[1]:
        c.value = c.value.replace("$", unit) if isinstance(c.value, str) else c.value


def instrument_options(ws, desk):
    # Each trade journal has a distinct instrument universe.
    for rule in ws.data_validations.dataValidation:
        if str(rule.sqref).startswith("C2:"):
            choices = {"Форекс":"Спот FX,CFD", "Крипта":"Спот,Дериватив", "Інвестиції":"Акції,Облігації,ETF,Сировина,Ф’ючерси"}
            rule.formula1 = '"' + choices[desk] + '"'


def journal(ws, desk, unit, idx):
    is_bet = desk == "Ставки"
    if is_bet:
        core.bets(ws)
        extra = ["Спорт", "Майданчик", "Обґрунтування до дії", "Джерело / URL", "Час даних", "Коли теза хибна",
                 "Урок після результату", "Виплата покеру з урахуванням рейку", "ID новини", "Стан запису"]
        for rule in ws.data_validations.dataValidation:
            if str(rule.sqref).startswith("K2:"):
                rule.formula1 = '"Відкрита,Виграш,Програш,Повернення,Скасована,Розраховано"'
        options(ws, "Q", SPORTS)
        options(ws, "R", ["VBET", "Parimatch", "Інший", "Паперовий стіл"])
    else:
        core.trades(ws)
        extra = ["Горизонт / стратегія", "Джерело / URL", "Час даних", "Коли теза хибна", "Урок після результату",
                 "Плече", "ID новини", "Спред + прослизання у витратах", "Стан запису"]
        options(ws, "W", MODES)
        instrument_options(ws, desk)
    old = len(core.BET if is_bet else core.TRADE)
    for j, val in enumerate(extra, old+1):
        ws.cell(1, j, val)
    currency_headers(ws, unit)
    capital = f"'Налаштування'!$F${idx}"
    for i in range(2, LAST+1):
        if is_bet:
            previous = ws[f"N{i}"].value[1:]
            ws[f"N{i}"] = f'=IF(Q{i}="Покер",IF(AND(K{i}="Розраховано",J{i}>0,ISNUMBER(X{i}),X{i}>=0,ISNUMBER(B{i}),ISNUMBER(P{i}),P{i}>=B{i}),X{i}-J{i},""),{previous})'
            ws[f"Z{i}"] = f'=IF(A{i}="","",IF(AND(C{i}<>"",D{i}<>"",Q{i}<>"",R{i}<>"",S{i}<>"",T{i}<>"",ISNUMBER(U{i}),U{i}<=B{i},V{i}<>""),"Описано","Доповнити"))'
            ws[f"U{i}"].number_format = core.TIME
        else:
            for c in ["L","V"]:
                cell = ws[f"{c}{i}"]
                cell.value = cell.value.replace(core.DEP, capital)
            ws[f"AE{i}"] = f'=IF(A{i}="","",IF(AND(Q{i}<>"",X{i}<>"",ISNUMBER(Y{i}),Y{i}<=B{i},Z{i}<>"",W{i}<>"",AB{i}>=1,AB{i}<=\'Налаштування\'!$B$12,R{i}<>"",D{i}<>"",C{i}<>""),"Описано","Доповнити"))'
            ws[f"Y{i}"].number_format = core.TIME
    ws.auto_filter.ref = ws.dimensions
    style(ws)
    for col in (["S","T","V","W"] if is_bet else ["Q","X","Z","AA"]):
        ws.column_dimensions[col].width = 36


def period_row(ws, row, label, offset, length, bank):
    start = f"B{row}"
    end = f"C{row}"
    ws[f"A{row}"] = label
    ws[start] = f'=IF(ISNUMBER({START}),{START}+{offset},"")'
    ws[end] = f'=IF(ISNUMBER({start}),{start}+{length}-1,"")'
    times = f"$R$2:$R${LAST}"
    pnl = f"$S$2:$S${LAST}"
    records = f'{times},">="&{start},{times},"<"&({end}+1)'
    def put(col, expr):
        ws[f"{col}{row}"] = f'=IF(ISNUMBER({start}),{expr},"")'
    put("D", f'COUNTIFS({records})')
    put("E", f'IF(D{row}>0,SUMIFS({pnl},{records}),"")')
    put("F", f'IFERROR(COUNTIFS({records},{pnl},">0")/D{row},"")')
    put("G", f'IFERROR(-SUMIFS({pnl},{records},{pnl},">0")/SUMIFS({pnl},{records},{pnl},"<0"),"")')
    put("H", f'IFERROR(AVERAGEIFS($T$2:$T${LAST},{records}),"")')
    begin = f'1+COUNTIFS({times},">0",{times},"<"&{start})'
    dd = f'$V$2:$V${LAST}'
    put("I", f'IF(D{row}>0,MAX(INDEX({dd},{begin}):INDEX({dd},{begin}+D{row}-1)),"")')
    put("J", f'IFERROR(AVERAGEIFS($U$2:$U${LAST},{records}),"")')
    if label == "День":
        put("K", f'IF(D{row}>0,{bank}+SUM(E$2:E{row}),"")')
    for c in "BC":
        ws[f"{c}{row}"].number_format = core.DATE
    for c in "FIJ":
        ws[f"{c}{row}"].number_format = core.PCT


def analytics(ws, desk, idx):
    bank = f"'Налаштування'!$F${idx}"
    bet = desk == "Ставки"
    src = f"'{desk}'!"
    when, pnl, risk, audit = ("P","N","O","Z") if bet else ("T","O","P","AE")
    header(ws, ["Період", "Від", "До", "Закрито", "P&L", "Виграшні", "Profit factor", "Очікування R", "Просадка", "CLV", "Баланс дня"])
    for i in range(2, LAST+1):
        stamp = f"{src}{when}{i}"
        value = f"{src}{pnl}{i}"
        ws[f"L{i}"] = f'=IF(AND({src}A{i}="ПАПІР",ISNUMBER({value}),{src}{audit}{i}="Описано",ISNUMBER({START}),{stamp}>={START},{stamp}<{START}+31),{stamp},"")'
        for col, source in [("M",value),("N",f"{src}{risk}{i}")]:
            ws[f"{col}{i}"] = f'=IF(ISNUMBER(L{i}),{source},"")'
        if bet:
            ws[f"O{i}"] = f'=IF(AND(ISNUMBER(L{i}),{src}Q{i}<>"Покер",ISNUMBER({src}M{i})),{src}M{i},"")'
        ws[f"P{i}"] = f'=IF(ISNUMBER(L{i}),COUNTIF(L$2:L${LAST},"<"&L{i})+COUNTIF(L$2:L{i},L{i}),"")'
        ws[f"Q{i}"] = f'=IFERROR(MATCH(ROW()-1,P$2:P${LAST},0),"")'
        for dest, orig in [("R","L"),("S","M"),("T","N")]:
            ws[f"{dest}{i}"] = f'=IF(ISNUMBER(Q{i}),INDEX({orig}$2:{orig}${LAST},Q{i}),"")'
        if bet:
            ws[f"U{i}"] = f'=IF(ISNUMBER(Q{i}),IF(ISNUMBER(INDEX(O$2:O${LAST},Q{i})),INDEX(O$2:O${LAST},Q{i}),""),"")'
        ws[f"W{i}"] = f'=IF(ISNUMBER(S{i}),{bank}+SUM(S$2:S{i}),"")'
        ws[f"V{i}"] = f'=IF(ISNUMBER(W{i}),1-W{i}/MAX({bank},W$2:W{i}),"")'
    for i in range(31):
        period_row(ws, i+2,"День", i, 1, bank)
    for i in range(5):
        period_row(ws, i+33,"Тиждень",7*i,min(7,31-7*i),bank)
    for i,n in enumerate([14,21,31],38):
        period_row(ws,i,("21 день" if n == 21 else f"{n} днів"),0,n,bank)
    ws["A42"] = "Критерії за 21 день"
    threshold = "'Налаштування'!$B$"
    min_count = threshold + ("9" if bet else "8")
    clv = f',ISNUMBER(J39),J39>={threshold}11' if bet else ""
    missing = f',COUNT({threshold}11)=0' if bet else ""
    ws["B42"] = f'=IF(OR(COUNT({START},{min_count},{threshold}10)<3{missing}),"Потрібні критерії",IF(TODAY()<C39+1,"Триває",IF(D39=0,"Немає даних",IF(AND(D39>={min_count},I39<={threshold}10{clv}),"Пройдено","Не пройдено"))))'
    style(ws)
    add_analytics_charts(ws)


def add_analytics_charts(ws):
    for col in range(12,24):
        ws.column_dimensions[letter(col)].hidden = True
    for chart_type, col, title, anchor in [(LineChart,11,"Баланс після закриття дня","A45"),(BarChart,5,"Денний результат","F45")]:
        chart = chart_type()
        chart.title = title
        chart.add_data(Reference(ws,min_col=col,min_row=1,max_row=32),titles_from_data=True)
        chart.set_categories(Reference(ws,min_col=2,min_row=2,max_row=32))
        chart.legend = None
        chart.width, chart.height = 13, 7
        ws.add_chart(chart,anchor)


def dashboard(ws):
    header(ws, ["Напрям", "Валюта", "Старт", "Закрито", "P&L", "Баланс", "Виграшні", "Profit factor", "Очікування R", "Просадка", "CLV", "Потребують опису"])
    for i,(desk,unit,_) in enumerate(DESKS,2):
        ws[f"A{i}"],ws[f"B{i}"] = desk,unit
        ws[f"C{i}"] = f"='Налаштування'!F{i}"
        ref = f"'Аналітика {desk}'!"
        for dst,source in [("D","D"),("E","E"),("G","F"),("H","G"),("I","H"),("J","I"),("K","J")]:
            addr = ref + source + "40"
            ws[f"{dst}{i}"] = f'=IF(ISNUMBER({addr}),{addr},"")'
        ws[f"F{i}"] = f'=C{i}+SUM(E{i})'
        quality = "Z" if desk=="Ставки" else "AE"
        ws[f"L{i}"] = f'=COUNTIFS(\'{desk}\'!A2:A{LAST},"ПАПІР",\'{desk}\'!{quality}2:{quality}{LAST},"Доповнити")'
        for c in "GJK":
            ws[f"{c}{i}"].number_format = core.PCT
    ws["A8"]="Вікно огляду"
    ws["B8"]="21 день"
    rule=DataValidation(type="list",formula1='"14 днів,21 день,31 день"')
    ws.add_data_validation(rule)
    rule.add("B8")
    ws["A10"],ws["B10"],ws["C10"],ws["D10"]="Напрям","Закрито","Очікування R","Просадка"
    for i,(desk,_,_) in enumerate(DESKS,11):
        ws[f"A{i}"]=desk
        for dest, source in [("B","D"),("C","H"),("D","I")]:
            rng=f"'{ 'Аналітика '+desk }'!{source}38:{source}40"
            pick=f'INDEX({rng},IF(B$8="14 днів",1,IF(B$8="21 день",2,3)))'
            ws[f"{dest}{i}"]=f'=IF(ISNUMBER({pick}),{pick},"")'
        ws[f"D{i}"].number_format=core.PCT
    chart=BarChart()
    chart.title="Кількість закритих записів за вибране вікно"
    chart.add_data(Reference(ws,min_col=2,min_row=10,max_row=14),titles_from_data=True)
    chart.set_categories(Reference(ws,min_col=1,min_row=11,max_row=14))
    chart.legend=None
    ws.add_chart(chart,"A17")
    style(ws)


def build(path: Path):
    wb=Workbook()
    main=wb.active
    main.title="Дашборд"
    configure(wb.create_sheet("Налаштування"))
    dashboard(main)
    for idx,(desk,unit,_) in enumerate(DESKS,2):
        journal(wb.create_sheet(desk),desk,unit,idx)
        analytics(wb.create_sheet("Аналітика "+desk),desk,idx)
    logs={
        "Новини FX та сесії":["ID новини","Заплановано · Київ","Фактичний час даних","Сесія / часовий пояс","Пара","Подія","Джерело / URL","Консенсус","Факт","Попереднє","Теза до релізу","Ризик спреду","Рядок угоди","Що вийшло"],
        "Досьє крипти":["Монета / мережа","Контракт / ідентифікатор","Заснування й засновники","Первинне джерело","Призначення і конкуренти","Емісія / розблокування","Концентрація / ліквідність","Управління і права ключів","Аудити / інциденти","Команда й конфлікти","Каталізатор","Сценарій втрати","Умови відмови","Висновок і невідоме","Перевірено · час"],
        "Інвестори та емітенти":["Особа / емітент","Країна / сектор","Дата факту","Дата публікації","Первинне розкриття","Документ / URL","Стратегія / експозиція","Що підтверджено","Що невідомо","Ризики й контрприклад","Наступний перегляд"],
        "Звіти Сема":["Дата й час","Ранок / вечір / подія","Напрям","Сесія / новини","Рішення і чому","Ризики","Посилання на запис","Помилка / альтернатива","Гіпотеза на перевірку","Результат звірки","Голос / текст"],
    }
    for name,fields in logs.items():
        ws=wb.create_sheet(name)
        header(ws,fields)
        style(ws)
        ws.auto_filter.ref=f"A1:{letter(len(fields))}{LAST}"
    guide=wb.create_sheet("Довідка")
    core.guide(guide)
    guide["B2"]="Постав дату старту, частку Келлі й власні критерії. Чотири незалежні паперові банки. Журнали мають по 200 рядків. Вікна 14, 21 та 31 день від старту."
    guide["B13"]="Кожний напрям має окремий банк і аналітику. До результату потрапляють лише розраховані рядки ПАПІР із попереднім обґрунтуванням, джерелом і часовою міткою. Потребують опису показано на дашборді."
    guide["B15"]="Просадка за закритими операціями від піку поточного банку. Нереалізований збиток відкритих позицій не входить. Гроші різних валют не додаються."
    guide["B16"]="Оцінка на 21-й день окремо за напрямом. Без погоджених критеріїв — статус «Потрібні критерії». Завершення оцінки не активує реальний рахунок."
    guide.append(["Паперова дія","У полі погодження можна вказати Сем · папір. Витрати включають комісію, своп і модельоване прослизання. Плече від 1 до 10. Ціна виконання має бути досяжною після часу рішення."])
    guide.append(["Покер","Один рядок — завершена сесія. Обери Покер та Розраховано. У паперову суму внеси бай-іни й ребаї, у виплату — суму повернення після рейку. CLV та Келлі для сесії не застосовуються."])
    guide.append(["Дані","Дашборд перераховується після зміни журналу. Передача від Сема й брокерські рахунки не підключені. Затримані та ручні дані позначай у джерелі. Дату та банківські реквізити реальних операцій сюди не внось."])
    style(guide)
    guide.column_dimensions["A"].width=35
    guide.column_dimensions["B"].width=103
    for cell in list(guide["B"])[1:]:
        cell.alignment=Alignment(wrap_text=True,vertical="center")
        guide.row_dimensions[cell.row].height=51
    core.examples(wb["Форекс"],wb["Ставки"])
    for r in (2,3):
        wb["Форекс"][f"C{r}"]="Спот FX"
        wb["Форекс"][f"D{r}"]="Умовна пара"
    wb["Ставки"]["Q2"]="Футбол"
    wb["Ставки"]["S2"]="Приклад оцінювання ймовірності"
    wb["Форекс"]["W2"]="Денна"
    wb["Форекс"]["W3"]="Новини"
    wb.save(path)
