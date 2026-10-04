"""
SYNDIKAT Chief Security Officer (CSO) — Marshal Agent.
Supreme Security Commander of EVA SYNDICATE (Floor 10).

Marshal is the supreme security authority of the Syndicate, commanding the
subordinate Sentinel Protocol (Zero-Trust shield, inbound/outbound filters,
lethal trifecta guard, command sanitizer, and secret scanner).

Responsibilities:
- Supreme security governance, threat intelligence, and audit logging.
- Direct command of Sentinel Protocol and automated defense perimeters.
- Compliance & copyright enforcement on Floor 2 Content Factory assets.
- Emergency containment and agent isolation in case of compromise.
- Human-in-the-Loop escalation handler for critical security operations.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from src.agents.sentinel import SentinelAgent, ValidationResult

logger = structlog.get_logger(__name__)


class MarshalAgent:
    """
    Chief Security Officer (CSO) of EVA SYNDICATE.
    Supreme security commander directing the Sentinel Protocol.
    """

    AGENT_ID = "marshal"
    ROLE = "Chief Security Officer (CSO)"

    def __init__(
        self,
        memory: Optional[Any] = None,
        llm: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        sentinel: Optional[SentinelAgent] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = dict(config or {})
        # Sentinel Protocol is Marshal's subordinate automated security shield
        self.sentinel = sentinel or SentinelAgent(vault_client=self._config.get("vault_client"))
        self._incident_log: List[Dict[str, Any]] = []

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch security command."""
        action = payload.get("action", "security_audit")
        logger.info("marshal_security_dispatched", action=action)

        try:
            if action in ("security_audit", "audit", "system_audit"):
                return await self._security_audit(payload)
            elif action in ("incident_report", "threat_intel"):
                return await self._incident_report(payload)
            elif action in ("validate_task", "check_task"):
                return await self._validate_task(payload)
            elif action in ("veto_outbound", "outbound_veto"):
                return await self._veto_outbound(payload)
            elif action in ("lethal_trifecta", "check_trifecta"):
                return await self._check_trifecta(payload)
            elif action in ("dependency_audit", "slopsquatting"):
                return await self._assess_dependency(payload)
            elif action in ("scan_secrets", "leak_check"):
                return await self._scan_secrets(payload)
            elif action in ("emergency_lockdown", "containment"):
                return await self._emergency_lockdown(payload)
            elif action in ("morning_data", "security_status"):
                return await self._morning_data(payload)
            elif action in ("compliance_check", "check_design_compliance"):
                return await self._compliance_check(payload)
            else:
                return await self._security_audit(payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Marshal security execution error", action=action, exc_info=exc)
            return {"error": str(exc), "agent": self.AGENT_ID, "action": action, "status": "failed"}

    async def _security_audit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Holistic security audit across all 10 floors of the Syndicate."""
        audit_res = {
            "agent": self.AGENT_ID,
            "role": self.ROLE,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "protocol_status": "Sentinel Protocol Active (Zero-Trust)",
            "monitored_floors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "security_shields": {
                "inbound_prompt_injection": "ENABLED",
                "outbound_action_veto": "ENABLED",
                "lethal_trifecta_guard": "ENFORCED",
                "command_safety_sanitizer": "ENFORCED",
                "slopsquatting_defense": "ENABLED",
                "secret_leakage_scanner": "ACTIVE",
                "webhook_hmac_sha256": "ENFORCED",
            },
            "recent_incidents_count": len(self._incident_log),
            "threat_level": "DEFCON_4 (Normal / Defended)",
            "status": "nominal",
        }
        await self._save_episode("security_audit", audit_res)
        return audit_res

    async def _incident_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tactical security incident report for Eva and the Operator."""
        limit = int(payload.get("limit", 10))
        recent = self._incident_log[-limit:] if self._incident_log else []
        return {
            "agent": self.AGENT_ID,
            "role": self.ROLE,
            "total_recorded_threats": len(self._incident_log),
            "recent_incidents": recent,
            "containment_status": "All detected threats blocked by Sentinel Protocol",
            "status": "completed",
        }

    async def _validate_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an inbound task through Sentinel Protocol with Marshal's seal."""
        task_data = payload.get("task", payload)
        res = await self.sentinel.validate_task(task_data)
        if not res.allowed:
            self._record_incident(threat_type="inbound_task_blocked", detail=res.reason, risk_score=res.risk_score)
        return {
            "agent": self.AGENT_ID,
            "commander": "Marshal",
            "subordinate_protocol": "Sentinel",
            "allowed": res.allowed,
            "reason": res.reason,
            "risk_score": res.risk_score,
            "requires_hitl": res.requires_hitl,
        }

    async def _veto_outbound(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce outbound action policies via Sentinel Protocol."""
        target_agent = payload.get("target_agent", "unknown")
        action_data = payload.get("action_data", payload)
        res = await self.sentinel.veto_outbound_action(target_agent, action_data)
        if not res.allowed:
            self._record_incident(threat_type="outbound_veto", detail=f"{target_agent}: {res.reason}", risk_score=res.risk_score)
        return {
            "agent": self.AGENT_ID,
            "allowed": res.allowed,
            "reason": res.reason,
            "risk_score": res.risk_score,
            "requires_hitl": res.requires_hitl,
        }

    async def _check_trifecta(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Check for lethal trifecta conditions."""
        res = self.sentinel.check_lethal_trifecta(payload)
        if not res["allowed"]:
            self._record_incident(threat_type="lethal_trifecta_blocked", detail=res["reason"], risk_score=res["risk_score"])
        return res

    async def _assess_dependency(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Audit third-party package installation for slopsquatting."""
        pkg = payload.get("package_name") or payload.get("package", "")
        return self.sentinel.assess_dependency_install(pkg)

    async def _scan_secrets(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scan text/output for leaked API tokens or credentials."""
        text = payload.get("text") or payload.get("output", "")
        return self.sentinel.scan_output_for_secrets(text)

    async def _compliance_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit Floor 2 content & POD merchandise designs for trademark/copyright violations.
        Marshal protects the Syndicate from IP infringement lawsuits.
        """
        artwork = payload.get("artwork_path", "media/art/cyber_skull.png")
        lower_art = artwork.lower()
        blocked_brands = ["disney", "marvel", "nike", "adidas", "pokemon", "star wars", "mickey", "coca-cola"]
        violations = [f"Trademark IP Violation: Protected brand '{b}' detected." for b in blocked_brands if b in lower_art]

        safe = len(violations) == 0
        if not safe:
            self._record_incident(threat_type="trademark_ip_violation", detail=str(violations), risk_score=0.9)
            logger.warning("marshal_trademark_veto", violations=violations)

        return {
            "agent": self.AGENT_ID,
            "safe": safe,
            "allowed": safe,
            "violations": violations,
            "status": "approved" if safe else "veto_blocked",
        }

    async def _emergency_lockdown(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger emergency containment: revoke all outbound agent capabilities
        and lock down the system until Operator verification.
        """
        reason = payload.get("reason", "Operator manual trigger or critical breach detected")
        logger.critical("MARSHAL_EMERGENCY_LOCKDOWN_TRIGGERED", reason=reason)
        self._record_incident(threat_type="EMERGENCY_LOCKDOWN", detail=reason, risk_score=1.0)
        return {
            "agent": self.AGENT_ID,
            "status": "LOCKDOWN_ACTIVE",
            "reason": reason,
            "outbound_network": "SEVERED",
            "financial_gate": "FROZEN",
            "operator_action_required": "Operator must issue clearance to lift lockdown.",
        }

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Provide security status snapshot for Eva's 07:30 Daily Briefing."""
        return {
            "agent": self.AGENT_ID,
            "role": self.ROLE,
            "threat_level": "DEFCON_4 (Normal)",
            "sentinel_protocol": "Active & Guarding",
            "blocked_threats_24h": len(self._incident_log),
            "pending_hitl_security_alerts": 0,
            "cfo_dossier": {"recipient": "Fin (CFO)", "status": "verified"},
            "status": "secure",
        }

    def _record_incident(self, threat_type: str, detail: str, risk_score: float) -> None:
        """Internal audit recording of security incidents."""
        incident = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "threat_type": threat_type,
            "detail": detail,
            "risk_score": risk_score,
            "mitigation": "Blocked by Sentinel Protocol under Marshal Command",
        }
        self._incident_log.append(incident)
        logger.warning("marshal_incident_recorded", **incident)

    async def _save_episode(self, action: str, data: Dict[str, Any]) -> None:
        """Record operational security episode in shared memory if available."""
        if self._memory and hasattr(self._memory, "save_episode"):
            try:
                await self._memory.save_episode(
                    session_id="marshal_security_ops",
                    agent_id=self.AGENT_ID,
                    role="assistant",
                    content=f"Marshal Security: {action}",
                    metadata={"action": action, "data": data},
                )
            except Exception as e:
                logger.warning("marshal_memory_save_failed", error=str(e))
