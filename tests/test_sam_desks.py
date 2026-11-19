"""Exercise the four independent paper books and their dashboard."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from openpyxl import load_workbook

from tools.sam_sheet.desks import DESKS, LAST, build


class DeskWorkbookTest(TestCase):
    def test_desks_and_separate_money(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "desks.xlsx"
            build(path)
            wb = load_workbook(path)
            self.assertEqual(wb.sheetnames[0], "Дашборд")
            self.assertEqual(len(wb["Дашборд"]._charts), 1)
            self.assertIsNone(wb["Налаштування"]["B6"].value)
            for row, (name, unit, start) in enumerate(DESKS, 2):
                self.assertEqual(wb["Налаштування"][f"E{row}"].value, unit)
                self.assertEqual(wb["Налаштування"][f"F{row}"].value, start)
                chart_page = wb["Аналітика " + name]
                self.assertEqual(len(chart_page._charts), 2)
                self.assertIn('"ПАПІР"', chart_page["L2"].value)
                self.assertIn('"Описано"', chart_page[f"L{LAST}"].value)
                self.assertIn(f"'Налаштування'!$F${row}", chart_page["W2"].value)
                self.assertEqual(chart_page["A39"].value, "21 день")
            self.assertIn("X2-J2", wb["Ставки"]["N2"].value)
            self.assertIn("AB2", wb["Форекс"]["AE2"].value)
            self.assertIn("Покер", wb["Ставки"]["N2"].value)
            wb.close()
