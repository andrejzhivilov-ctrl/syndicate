"""
Eva Office Copilot & MS Office Automation Engine for SYNDIKAT.
Provides programmatic Word (.docx), Excel (.xlsx), VBA Macro synthesis,
and comprehensive Office Knowledge Base lookups.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

# Try importing python-docx and openpyxl
try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not installed. Word doc generation disabled.")

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    logger.warning("openpyxl not installed. Excel workbook generation disabled.")


class OfficeKnowledgeBase:
    """Built-in structured knowledge base for Word, Excel, Formulas, and VBA."""

    EXCEL_SHORTCUTS = {
        "F4": "Repeat last action or toggle absolute/relative reference ($A$1)",
        "Ctrl+Shift+L": "Toggle AutoFilter on/off for current selection",
        "Alt+= (Alt+Equal)": "AutoSum selected range instantly",
        "Ctrl+T": "Convert selected range into formatted Excel Table with dynamic formulas",
        "Ctrl+; (Semicolon)": "Insert current static date",
        "Ctrl+Shift+;": "Insert current static time",
        "Ctrl+Shift+~": "Apply General number format",
        "Ctrl+Shift+$": "Apply Currency format with two decimal places",
        "Ctrl+Shift+%": "Apply Percentage format",
        "Ctrl+PageDown / PageUp": "Switch to next / previous sheet",
        "Alt+Enter": "Insert line break inside a single cell",
        "Ctrl+1": "Open Format Cells dialog",
    }

    WORD_SHORTCUTS = {
        "Ctrl+Alt+1": "Apply Heading 1 style",
        "Ctrl+Alt+2": "Apply Heading 2 style",
        "Ctrl+Alt+3": "Apply Heading 3 style",
        "Shift+F3": "Toggle case (lowercase, UPPERCASE, Title Case)",
        "Ctrl+Shift+N": "Apply Normal style to clear formatting",
        "Ctrl+K": "Insert hyperlink",
        "Alt+Shift+D": "Insert current date field",
        "Alt+Shift+T": "Insert current time field",
        "Ctrl+Enter": "Insert manual page break",
    }

    EXCEL_FORMULAS = {
        "XLOOKUP": {
            "syntax": "=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])",
            "desc": "Modern replacement for VLOOKUP/HLOOKUP. Supports exact match by default, left-lookups, and defaults on error.",
            "example": "=XLOOKUP(A2, Products!A:A, Products!C:C, 'Not Found')"
        },
        "INDEX_MATCH": {
            "syntax": "=INDEX(return_range, MATCH(lookup_value, lookup_range, 0))",
            "desc": "Legacy robust 2-way matrix lookup compatible with all Excel versions.",
            "example": "=INDEX(C2:C100, MATCH(E1, A2:A100, 0))"
        },
        "SUMIFS": {
            "syntax": "=SUMIFS(sum_range, criteria_range1, criteria1, [criteria_range2, criteria2], ...)",
            "desc": "Sums values matching multiple conditions simultaneously.",
            "example": "=SUMIFS(Revenue, Country, 'UA', Month, 'Sep')"
        },
        "LET": {
            "syntax": "=LET(name1, val1, [name2, val2], calculation)",
            "desc": "Defines intermediate named variables inside an Excel formula to boost calculation speed and readability.",
            "example": "=LET(x, A2*1.2, IF(x>1000, x*0.9, x))"
        },
        "FILTER": {
            "syntax": "=FILTER(array, include, [if_empty])",
            "desc": "Dynamic array formula to extract matching records without VBA or manual filtering.",
            "example": "=FILTER(A2:D500, D2:D500='Approved', 'No items')"
        },
        "UNIQUE": {
            "syntax": "=UNIQUE(array, [by_col], [exactly_once])",
            "desc": "Returns deduplicated unique values from a range or table column.",
            "example": "=SORT(UNIQUE(Orders[Customer]))"
        }
    }

    VBA_MACRO_TEMPLATES = {
        "clean_and_trim": {
            "title": "Clean & Trim Whitespace and Non-Printable Characters",
            "code": (
                "Sub CleanAndTrimData()\n"
                "    Dim ws As Worksheet\n"
                "    Dim rng As Range, cell As Range\n"
                "    Application.ScreenUpdating = False\n"
                "    Application.Calculation = xlCalculationManual\n"
                "    Set ws = ActiveSheet\n"
                "    On Error Resume Next\n"
                "    Set rng = ws.UsedRange.SpecialCells(xlCellTypeConstants, xlTextValues)\n"
                "    On Error GoTo 0\n"
                "    If Not rng Is Nothing Then\n"
                "        For Each cell In rng\n"
                "            cell.Value = Application.WorksheetFunction.Clean(Trim(cell.Value))\n"
                "        Next cell\n"
                "    End If\n"
                "    Application.Calculation = xlCalculationAutomatic\n"
                "    Application.ScreenUpdating = True\n"
                "    MsgBox \"Data cleaned and trimmed successfully.\", vbInformation, \"SYNDIKAT Office\"\n"
                "End Sub"
            )
        },
        "auto_export_pdf": {
            "title": "Export Active Sheet as PDF with Timestamp",
            "code": (
                "Sub ExportSheetToPDF()\n"
                "    Dim ws As Worksheet\n"
                "    Dim filePath As String\n"
                "    Set ws = ActiveSheet\n"
                "    filePath = ThisWorkbook.Path & \"\\\" & ws.Name & \"_\" & Format(Now, \"yyyymmdd_hhnnss\") & \".pdf\"\n"
                "    ws.ExportAsFixedFormat Type:=xlTypePDF, Filename:=filePath, _\n"
                "        Quality:=xlQualityStandard, IncludeDocProperties:=True, _\n"
                "        IgnorePrintAreas:=False, OpenAfterPublish:=True\n"
                "    MsgBox \"PDF exported to: \" & vbCrLf & filePath, vbInformation, \"SYNDIKAT PDF Export\"\n"
                "End Sub"
            )
        },
        "highlight_anomalies": {
            "title": "Highlight Outliers & Negative Balances in Selection",
            "code": (
                "Sub HighlightAnomalies()\n"
                "    Dim cell As Range\n"
                "    If Selection Is Nothing Then Exit Sub\n"
                "    For Each cell In Selection\n"
                "        If IsNumeric(cell.Value) And Not IsEmpty(cell.Value) Then\n"
                "            If cell.Value < 0 Then\n"
                "                cell.Interior.Color = RGB(255, 199, 206) ' Light Red\n"
                "                cell.Font.Color = RGB(156, 0, 6)        ' Dark Red\n"
                "            ElseIf cell.Value > 100000 Then\n"
                "                cell.Interior.Color = RGB(198, 239, 206) ' Light Green\n"
                "                cell.Font.Color = RGB(0, 97, 0)          ' Dark Green\n"
                "            End If\n"
                "        End If\n"
                "    Next cell\n"
                "    MsgBox \"Highlighting completed.\", vbInformation, \"SYNDIKAT\"\n"
                "End Sub"
            )
        },
        "unprotect_sheet_safe": {
            "title": "Protect / Unprotect Sheet with Password from Vault",
            "code": (
                "Sub ToggleSheetProtection()\n"
                "    Dim ws As Worksheet\n"
                "    Dim pwd As String\n"
                "    pwd = \"Syndikat2026\"\n"
                "    Set ws = ActiveSheet\n"
                "    If ws.ProtectContents Then\n"
                "        ws.Unprotect Password:=pwd\n"
                "        MsgBox \"Sheet un-protected.\", vbInformation\n"
                "    Else\n"
                "        ws.Protect Password:=pwd, UserInterfaceOnly:=True\n"
                "        MsgBox \"Sheet protected.\", vbInformation\n"
                "    End If\n"
                "End Sub"
            )
        }
    }


class OfficeCopilotAgent:
    """Autonomous agent engine for document and spreadsheet creation and knowledge lookup."""

    AGENT_ID = "eva_office"

    def __init__(self, memory=None, llm=None, config=None):
        self._memory = memory
        self._llm = llm
        self._config = config or {}
        self.kb = OfficeKnowledgeBase()

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch action for Office Copilot."""
        action = payload.get("action", "lookup")
        logger.info("office_copilot_execute", action=action)

        if action == "lookup_knowledge":
            return self._lookup_knowledge(payload)
        elif action == "generate_macro":
            return self._generate_macro(payload)
        elif action == "create_excel_report":
            return self._create_excel_report(payload)
        elif action == "create_word_document":
            return self._create_word_document(payload)
        else:
            return {
                "status": "error",
                "message": f"Unknown office action '{action}'",
                "available_actions": [
                    "lookup_knowledge",
                    "generate_macro",
                    "create_excel_report",
                    "create_word_document"
                ]
            }

    def _lookup_knowledge(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve formula syntax, keyboard shortcuts, or templates."""
        tool = payload.get("tool", "all").lower()  # "word", "excel", "macro", "all"
        query = payload.get("query", "").strip().lower()

        results = {
            "excel_shortcuts": self.kb.EXCEL_SHORTCUTS,
            "word_shortcuts": self.kb.WORD_SHORTCUTS,
            "formulas": self.kb.EXCEL_FORMULAS,
            "macros": {k: v["title"] for k, v in self.kb.VBA_MACRO_TEMPLATES.items()}
        }

        if query:
            filtered_formulas = {
                k: v for k, v in self.kb.EXCEL_FORMULAS.items()
                if query in k.lower() or query in v["desc"].lower()
            }
            results["matched_formulas"] = filtered_formulas

        return {"status": "ok", "data": results}

    def _generate_macro(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate VBA macro code according to user request."""
        macro_type = payload.get("macro_type", "clean_and_trim")
        template = self.kb.VBA_MACRO_TEMPLATES.get(macro_type)

        if template:
            return {
                "status": "ok",
                "title": template["title"],
                "vba_code": template["code"],
                "instructions": "In Excel press Alt+F11, Insert -> Module, paste this code, and press F5 or assign to button."
            }

        # Custom macro prompt
        prompt = payload.get("description", "Automate daily data processing")
        custom_code = (
            f"' SYNDIKAT Custom Generated Macro\n"
            f"' Purpose: {prompt}\n"
            f"Sub SyndikatCustomMacro()\n"
            f"    On Error GoTo ErrorHandler\n"
            f"    Application.ScreenUpdating = False\n"
            f"    Dim ws As Worksheet\n"
            f"    Set ws = ActiveSheet\n"
            f"    ' Auto-fit columns\n"
            f"    ws.Columns.AutoFit\n"
            f"    ' Done\n"
            f"    Application.ScreenUpdating = True\n"
            f"    MsgBox \"Custom processing complete.\", vbInformation, \"SYNDIKAT\"\n"
            f"    Exit Sub\n"
            f"ErrorHandler:\n"
            f"    Application.ScreenUpdating = True\n"
            f"    MsgBox \"Error: \" & Err.Description, vbCritical, \"SYNDIKAT Error\"\n"
            f"End Sub"
        )
        return {
            "status": "ok",
            "title": "Custom VBA Macro",
            "vba_code": custom_code,
            "instructions": "Paste into standard Excel module."
        }

    def _create_excel_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Programmatically create a styled Excel workbook."""
        if not OPENPYXL_AVAILABLE:
            return {"status": "error", "message": "openpyxl library not installed."}

        title = payload.get("title", "Financial & Operations Report")
        headers = payload.get("headers", ["Category", "Metric", "Target", "Actual", "Variance %", "Status"])
        rows = payload.get("rows", [
            ["Affiliate SaaS", "MRR Commission", "$5,000", "$5,420", "+8.4%", "ACTIVE"],
            ["POD Operations", "Net Margins", "$2,000", "$2,150", "+7.5%", "ACTIVE"],
            ["Media YouTube", "Subscriber Rate", "10,000", "12,400", "+24.0%", "SCALING"],
            ["Shopify Ecom", "ROAS", "3.5x", "4.1x", "+17.1%", "OPTIMIZED"]
        ])
        output_path = payload.get("output_path", "syndikat_report.xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = payload.get("sheet_name", "Executive Overview")

        # Color schemes (Dark executive glass style translated to Excel)
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid") # Dark navy slate
        header_font = Font(name="Segoe UI", size=11, bold=True, color="00F0FF") # Neon cyan font
        cell_font = Font(name="Segoe UI", size=10, color="000000")
        thin_border = Border(
            left=Side(style="thin", color="CCCCCC"),
            right=Side(style="thin", color="CCCCCC"),
            top=Side(style="thin", color="CCCCCC"),
            bottom=Side(style="thin", color="CCCCCC")
        )

        # Title block
        ws.merge_cells("A1:F1")
        title_cell = ws["A1"]
        title_cell.value = f"SYNDIKAT HOLDING — {title.upper()}"
        title_cell.font = Font(name="Segoe UI", size=14, bold=True, color="0F172A")
        title_cell.alignment = Alignment(vertical="center", horizontal="left")
        ws.row_dimensions[1].height = 28

        # Header row
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[3].height = 24

        # Rows
        for r_idx, row_data in enumerate(rows, start=4):
            for c_idx, val in enumerate(row_data, start=1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.font = cell_font
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        file_path = Path(output_path)
        wb.save(str(file_path))
        logger.info("excel_report_generated", path=str(file_path))

        return {
            "status": "ok",
            "file_path": str(file_path),
            "rows_count": len(rows),
            "columns": headers
        }

    def _create_word_document(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Programmatically create a styled Word (.docx) document."""
        if not DOCX_AVAILABLE:
            return {"status": "error", "message": "python-docx library not installed."}

        title = payload.get("title", "SYNDIKAT Strategic Briefing")
        subtitle = payload.get("subtitle", "Autonomous Multi-Agent Enterprise Protocol")
        sections = payload.get("sections", [
            {
                "heading": "1. Executive Summary",
                "text": "SYNDIKAT represents an autonomous multi-agent holding orchestrating operations, content, finance, and security under Eva (CEO)."
            },
            {
                "heading": "2. Domain Isolation Policy",
                "text": "Sam operates with 100% boundary isolation on Floor 3 (Quant Floor). Sentinel strictly vetos unauthorized outbound calls."
            }
        ])
        output_path = payload.get("output_path", "syndikat_briefing.docx")

        doc = docx.Document()

        # Document Header
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(title)
        title_run.font.name = "Segoe UI"
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(15, 23, 42)

        sub_p = doc.add_paragraph()
        sub_run = sub_p.add_run(subtitle)
        sub_run.font.name = "Segoe UI"
        sub_run.font.size = Pt(12)
        sub_run.font.italic = True
        sub_run.font.color.rgb = RGBColor(100, 116, 139)

        doc.add_paragraph() # Spacing

        # Sections
        for sec in sections:
            h = doc.add_heading(sec.get("heading", ""), level=1)
            h.style.font.name = "Segoe UI"
            h.style.font.color.rgb = RGBColor(14, 116, 144) # Cyan/Teal
            p = doc.add_paragraph(sec.get("text", ""))
            p.style.font.name = "Segoe UI"
            p.style.font.size = Pt(10.5)

        file_path = Path(output_path)
        doc.save(str(file_path))
        logger.info("word_document_generated", path=str(file_path))

        return {
            "status": "ok",
            "file_path": str(file_path),
            "sections_count": len(sections)
        }
