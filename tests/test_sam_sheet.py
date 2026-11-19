"""Validate the generated artifact without requiring a spreadsheet application."""
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import TestCase

from openpyxl import load_workbook
from openpyxl.formula.tokenizer import Tokenizer

from tools.sam_sheet.build import END, LAST, build


class SamSheetTest(TestCase):
    def test_paper_template(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "paper.xlsx"
            build(path)
            wb = load_workbook(path)
            self.assertEqual(wb.sheetnames, ["Налаштування", "Угоди", "Ставки", "Підсумки", "Довідка"])
            setup, trades, bets, summary, _ = wb.worksheets
            for row in (2, 6, 7, 8, 9, 10, 11):
                self.assertIsNone(setup[f"B{row}"].value)
            self.assertEqual([setup[f"B{i}"].value for i in (3, 4, 5)], [.01, -.03, 2.5])
            examples = [cell.value for ws in (trades, bets) for cell in ws["A"][1:] if cell.value]
            self.assertEqual(examples, ["ПРИКЛАД"] * 3)
            self.assertEqual(len(trades.data_validations.dataValidation), 4)
            self.assertEqual(len(bets.data_validations.dataValidation), 2)
            self.assertIn(f"O{LAST}/K{LAST}", trades[f"P{LAST}"].value)
            self.assertIn("E2/L2-1", bets["M2"].value)
            self.assertIn('"ПАПІР"', summary["P2"].value)
            self.assertIn(f"'Ставки'!A{LAST}", summary[f"P{END}"].value)
            self.assertIn("EDATE", summary["B40"].value)
            self.assertTrue(summary.conditional_formatting)
            for ws in wb:
                for row in ws:
                    for cell in row:
                        if cell.data_type == "f":
                            self.assertTrue(Tokenizer(cell.value).items)
            wb.close()
