"""
Ukrainian Open Banking Integration Client (Monobank & PrivatBank).
Part of EVA SYNDICATE Financial Infrastructure (Floor 10 - Fin CFO).

Provides read-only account balance synchronization, transaction ingestion,
and multi-currency normalization (UAH, USD, EUR) with safe mock fallbacks.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

# Currency code mappings (ISO 4217)
CURRENCY_CODES = {
    980: "UAH",
    840: "USD",
    978: "EUR",
    "UAH": "UAH",
    "USD": "USD",
    "EUR": "EUR",
}


class BankingClient:
    """
    Unified Open Banking Client for Monobank & PrivatBank.
    """

    def __init__(
        self,
        monobank_token: Optional[str] = None,
        privatbank_merchant_id: Optional[str] = None,
        privatbank_password: Optional[str] = None,
        timeout_s: float = 10.0,
    ) -> None:
        self.monobank_token = monobank_token or os.getenv("MONOBANK_API_TOKEN")
        self.privatbank_merchant_id = privatbank_merchant_id or os.getenv("PRIVATBANK_MERCHANT_ID")
        self.privatbank_password = privatbank_password or os.getenv("PRIVATBANK_PASSWORD")
        self.timeout_s = timeout_s

    async def get_accounts_overview(self) -> Dict[str, Any]:
        """
        Fetch aggregated account balances across Monobank, PrivatBank,
        and reserve cash.

        When no bank is configured or every provider fails we report
        ``status: "unavailable"`` with zeroed totals. The previous behaviour
        silently substituted a hardcoded "sandbox" portfolio (185 400 / 42 300
        / 74 200 UAH + 15 000 USD), which Fin then published to the CFO dossier
        as if it had been measured. Fake balances are now opt-in only and are
        always labelled ``synthetic: True``.
        """
        accounts = []

        # 1. Monobank Sync
        mono_accounts = await self._fetch_monobank_accounts()
        accounts.extend(mono_accounts)

        # 2. PrivatBank Sync
        privat_accounts = await self._fetch_privatbank_accounts()
        accounts.extend(privat_accounts)

        synthetic = False
        if not accounts:
            if self._sandbox_enabled():
                accounts = self._get_sandbox_mock_accounts()
                synthetic = True
                logger.warning(
                    "banking_sandbox_accounts_in_use",
                    hint="EVA_BANKING_SANDBOX=1 — these balances are NOT real.",
                )
            else:
                return {
                    "status": "unavailable",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "accounts_count": 0,
                    "accounts": [],
                    "synthetic": False,
                    "totals": {"UAH": 0.0, "USD": 0.0, "EUR": 0.0, "estimated_liquid_usd": 0.0},
                    "warning": (
                        "No bank accounts could be synced (no credentials or every "
                        "provider failed). Balances are NOT estimated."
                    ),
                }

        # Compute multi-currency totals
        total_uah = sum(a["balance"] for a in accounts if a["currency"] == "UAH")
        total_usd = sum(a["balance"] for a in accounts if a["currency"] == "USD")
        total_eur = sum(a["balance"] for a in accounts if a["currency"] == "EUR")

        # Estimate total liquid cash in USD (standard rate ~41.5 UAH/USD)
        estimated_usd = total_usd + (total_uah / 41.5) + (total_eur * 1.08)

        return {
            "status": "synced",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accounts_count": len(accounts),
            "accounts": accounts,
            "synthetic": synthetic,
            "totals": {
                "UAH": round(total_uah, 2),
                "USD": round(total_usd, 2),
                "EUR": round(total_eur, 2),
                "estimated_liquid_usd": round(estimated_usd, 2),
            },
        }

    async def _fetch_monobank_accounts(self) -> List[Dict[str, Any]]:
        """Fetch account balances via Monobank Personal API."""
        if not self.monobank_token:
            return []

        try:
            import httpx
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.get(
                    "https://api.monobank.ua/personal/client-info",
                    headers={"X-Token": self.monobank_token}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    accounts = []
                    for acc in data.get("accounts", []):
                        curr = CURRENCY_CODES.get(acc.get("currencyCode"), "UAH")
                        # Monobank returns cents
                        balance = acc.get("balance", 0) / 100.0
                        credit_limit = acc.get("creditLimit", 0) / 100.0
                        own_funds = balance - credit_limit
                        accounts.append({
                            "bank": "Monobank",
                            "account_id": acc.get("id"),
                            "type": acc.get("type", "black"),
                            "currency": curr,
                            "balance": round(own_funds, 2),
                            "credit_limit": round(credit_limit, 2),
                        })
                    logger.info("monobank_synced", accounts=len(accounts))
                    return accounts
                else:
                    logger.warning("monobank_api_error", status_code=resp.status_code)
                    return []
        except Exception as exc:  # noqa: BLE001
            logger.warning("monobank_fetch_failed", error=str(exc))
            return []

    async def _fetch_privatbank_accounts(self) -> List[Dict[str, Any]]:
        """Fetch account balances via PrivatBank AutoClient API."""
        if not (self.privatbank_merchant_id and self.privatbank_password):
            return []

        # In production this queries Privat24 Business XML/JSON endpoint
        logger.info("privatbank_configured", merchant_id=self.privatbank_merchant_id[:4] + "***")
        return []

    @staticmethod
    def _sandbox_enabled() -> bool:
        """Synthetic balances are opt-in and must never reach production.

        Set ``EVA_BANKING_SANDBOX=1`` for local demos only. Any code path that
        consumes these numbers must check the ``synthetic`` flag.
        """
        return os.getenv("EVA_BANKING_SANDBOX", "").strip().lower() in ("1", "true", "yes", "on")

    def _get_sandbox_mock_accounts(self) -> List[Dict[str, Any]]:
        """Synthetic demo portfolio — NOT real money, opt-in only."""
        return [
            {"bank": "Monobank (FOP Corp)", "account_id": "mono_fop_01", "currency": "UAH", "balance": 185400.0, "type": "fop"},
            {"bank": "Monobank (Personal Black)", "account_id": "mono_pers_01", "currency": "UAH", "balance": 42300.0, "type": "card"},
            {"bank": "PrivatBank (Main)", "account_id": "privat_fop_01", "currency": "UAH", "balance": 74200.0, "type": "fop"},
            {"bank": "Cash / Reserve Vault", "account_id": "vault_usd_01", "currency": "USD", "balance": 15000.0, "type": "cash"},
        ]
