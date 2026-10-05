"""
Fin Agent — Chief Financial Officer (CFO).
Handles cash flow tracking, runway calculation, bank data aggregation (Monobank/PrivatBank),
tax deadlines (DPS), budget limits, and financial reports.
"""

from __future__ import annotations

import json
from datetime import datetime, date
from typing import Any, Dict, Optional
import structlog
from src.memory import MemoryManager

logger = structlog.get_logger(__name__)


class FinAgent:
    """Financial analysis specialist agent and Chief Financial Officer."""
    AGENT_ID = "fin"

    def __init__(
        self,
        memory: MemoryManager,
        llm: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = dict(config or {})
        self._registry = registry

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute financial action based on payload."""
        action = payload.get("action", "analyze")
        try:
            if action in ("analyze", "financial_analysis"):
                return await self._analyze(payload.get("data", payload))
            elif action == "runway":
                return await self._calculate_runway(payload)
            elif action == "budget_check":
                return await self._check_budget(payload)
            elif action == "tax_radar":
                return await self._tax_radar(payload)
            elif action == "sync_bank_data":
                return await self._sync_bank_data(payload)
            elif action == "morning_data":
                return await self._morning_data(payload)
            elif action == "report":
                return await self._generate_report(payload)
            else:
                return {"error": f"Unknown action: {action}", "agent": self.AGENT_ID}
        except Exception as exc:  # noqa: BLE001
            logger.exception("FinAgent action execution error", action=action, exc_info=exc)
            return {"error": str(exc), "agent": self.AGENT_ID}

    async def _calculate_runway(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate survival runway in months/days.
        Runway = Total Liquid Cash / Monthly Burn Rate
        """
        total_balance = float(payload.get("cash_balance", payload.get("total_balance", payload.get("balance", payload.get("liquid_assets", 0.0)))))
        monthly_burn = float(payload.get("monthly_burn", 0.0))
        daily_burn = float(payload.get("daily_burn", 0.0))

        if monthly_burn <= 0 and daily_burn > 0:
            monthly_burn = daily_burn * 30.0

        if monthly_burn > 0:
            runway_months: Optional[float] = round(total_balance / monthly_burn, 1)
            runway_days: Optional[int] = int((total_balance / monthly_burn) * 30.4)
            status = (
                "healthy" if runway_months >= 6.0
                else "warning" if runway_months >= 3.0
                else "critical"
            )
            alert = "Low runway buffer: less than 3 months!" if status == "critical" else None
        else:
            # Previously reported 999 months / 9999 days — a fabricated
            # "infinite runway". Report the gap honestly instead.
            runway_months = None
            runway_days = None
            status = "unknown"
            alert = "Runway not computable: monthly_burn must be greater than 0."

        return {
            "agent": self.AGENT_ID,
            "total_balance": total_balance,
            "monthly_burn": monthly_burn,
            "runway_months": runway_months,
            "runway_days": runway_days,
            "status": status,
            "alert": alert,
        }

    async def _check_budget(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate expense proposal against current category budget limits.
        """
        category = payload.get("category", "general")
        amount = float(payload.get("amount", 0.0))
        currency = payload.get("currency", "UAH")
        limit = float(payload.get("category_limit", 15000.0))
        current_spent = float(payload.get("current_spent", 0.0))

        projected = current_spent + amount
        within_budget = projected <= limit
        remaining = max(0.0, limit - projected)

        return {
            "agent": self.AGENT_ID,
            "category": category,
            "amount": amount,
            "currency": currency,
            "within_budget": within_budget,
            "current_spent": current_spent,
            "category_limit": limit,
            "remaining": remaining,
            "requires_hitl": not within_budget or amount > 5000.0,
            "risk_level": "medium" if not within_budget else "low",
        }

    async def _tax_radar(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check upcoming tax payment and declaration deadlines (FOP 3rd group / Ukraine).
        """
        # FOP Group 3: Single Tax (5%) quarterly + ESV monthly/quarterly
        today = date.today()
        deadlines = [
            {"name": "ЄСВ за 1 квартал", "due": f"{today.year}-04-19", "type": "tax"},
            {"name": "Єдиний податок за 1 квартал", "due": f"{today.year}-05-19", "type": "tax"},
            {"name": "ЄСВ за 2 квартал", "due": f"{today.year}-07-19", "type": "tax"},
            {"name": "Єдиний податок за 2 квартал", "due": f"{today.year}-08-19", "type": "tax"},
            {"name": "ЄСВ за 3 квартал", "due": f"{today.year}-10-19", "type": "tax"},
            {"name": "Єдиний податок за 3 квартал", "due": f"{today.year}-11-19", "type": "tax"},
            {"name": "ЄСВ за 4 квартал", "due": f"{today.year+1}-01-19", "type": "tax"},
            {"name": "Єдиний податок за 4 квартал", "due": f"{today.year+1}-02-19", "type": "tax"},
        ]

        upcoming = []
        for d in deadlines:
            due_dt = datetime.strptime(d["due"], "%Y-%m-%d").date()
            days_left = (due_dt - today).days
            if 0 <= days_left <= 45:
                upcoming.append({**d, "days_left": days_left})

        return {
            "agent": self.AGENT_ID,
            "upcoming_taxes": upcoming,
            "count": len(upcoming),
            "urgent": any(d["days_left"] <= 7 for d in upcoming),
        }

    async def _sync_bank_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate accounts from Monobank, PrivatBank or manual statements using BankingClient.
        """
        if "accounts" in payload:
            accounts = payload["accounts"]
            total_uah = sum(float(a.get("balance", 0.0)) for a in accounts if a.get("currency") == "UAH")
            total_usd = sum(float(a.get("balance", 0.0)) for a in accounts if a.get("currency") == "USD")
            return {
                "agent": self.AGENT_ID,
                "status": "ok",
                "synced_at": datetime.now().isoformat(),
                "accounts": accounts,
                "total_uah": total_uah,
                "total_usd": total_usd,
            }

        # SAFETY RULE (mirrors Doc's "never fabricate medical data"):
        # when the banking integration is unreachable we MUST NOT invent account
        # balances — the CFO dossier and the runway figure would be built on
        # fabricated numbers. Report the failure explicitly instead.
        try:
            from src.integrations.banking import BankingClient
            client = BankingClient(
                monobank_token=self._config.get("monobank_api_token"),
                privatbank_merchant_id=self._config.get("privatbank_merchant_id"),
                privatbank_password=self._config.get("privatbank_password"),
            )
            overview = await client.get_accounts_overview()
            return {
                "agent": self.AGENT_ID,
                "status": "ok",
                "synced_at": overview["timestamp"],
                "accounts": overview["accounts"],
                "total_uah": overview["totals"]["UAH"],
                "total_usd": overview["totals"]["USD"],
                "estimated_liquid_usd": overview["totals"]["estimated_liquid_usd"],
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("banking_client_sync_unavailable", error=str(exc))
            return {
                "agent": self.AGENT_ID,
                "status": "unavailable",
                "synced_at": datetime.now().isoformat(),
                "accounts": [],
                "total_uah": 0.0,
                "total_usd": 0.0,
                "estimated_liquid_usd": 0.0,
                "error": f"banking_sync_unavailable: {exc}",
                "warning": (
                    "No live bank data available. Balances are NOT estimated — "
                    "supply 'accounts' in the payload or restore the banking integration."
                ),
            }

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Compact metrics for Eva's 07:00 Daily Briefing."""
        bank_data = await self._sync_bank_data(payload)
        runway_data = await self._calculate_runway({
            "total_balance": bank_data["total_uah"],
            "monthly_burn": 35000.0,
        })
        tax_data = await self._tax_radar(payload)

        return {
            "agent": self.AGENT_ID,
            "status": "ok" if bank_data.get("status", "ok") == "ok" else "degraded",
            "balance_uah": bank_data["total_uah"],
            "balance_usd": bank_data["total_usd"],
            "runway_days": runway_data["runway_days"],
            "runway_months": runway_data["runway_months"],
            "tax_alerts_count": len(tax_data["upcoming_taxes"]),
            "urgent_tax": tax_data["urgent"],
            **({"warning": bank_data["warning"]} if bank_data.get("warning") else {}),
        }

    async def _analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self._llm:
            return {
                "analysis": "LLM not configured. Deterministic analysis: metrics extracted.",
                "data_summary": {k: type(v).__name__ for k, v in data.items()},
                "agent": self.AGENT_ID,
            }
        from langchain_core.messages import HumanMessage
        response = await self._llm.ainvoke([
            HumanMessage(content=f"You are the CFO. Analyze the following financial data and provide strategic insights and risk flags:\n{json.dumps(data, ensure_ascii=False)}")
        ])
        return {"analysis": response.content, "agent": self.AGENT_ID}

    async def _generate_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        period = payload.get("period", "monthly")
        morning = await self._morning_data(payload)
        
        report_text = (
            f"📊 ФІНАНСОВИЙ ЗВІТ ({period.upper()})\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Загальний баланс UAH: {morning['balance_uah']:,.2f} грн\n"
            f"💵 Валютний резерв USD: ${morning['balance_usd']:,.2f}\n"
            f"⏳ Runway: {morning['runway_months']} міс ({morning['runway_days']} днів)\n"
            f"📌 Податкові дедлайни: {morning['tax_alerts_count']} на горизонті 45 днів\n"
        )
        return {"report": report_text, "metrics": morning, "agent": self.AGENT_ID}
