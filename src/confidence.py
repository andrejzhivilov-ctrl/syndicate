from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class EscalationLevel(Enum):
    ACT = "ACT"
    ASK = "ASK"
    REFUSE = "REFUSE"


@dataclass
class ConfidenceConfig:
    act_threshold: float
    ask_threshold: float
    risk_penalties: Dict[str, float]


@dataclass
class EscalationResult:
    level: EscalationLevel
    confidence: float
    adjusted_threshold: float
    reason: str
    action_risk: str


class ConfidenceBudget:
    """
    Confidence Budget & Escalation Protocol. Unified trust system for all agents.
    """
    def __init__(
        self,
        default_config: Optional[ConfidenceConfig] = None,
        agent_configs: Optional[Dict[str, ConfidenceConfig]] = None
    ) -> None:
        self.default_config = default_config or ConfidenceConfig(
            act_threshold=0.85,
            ask_threshold=0.50,
            risk_penalties={
                "critical": 0.2,
                "high": 0.1,
                "medium": 0.05,
                "low": 0.0
            }
        )
        
        self.agent_configs = agent_configs or {
            "sam": ConfidenceConfig(act_threshold=1.0, ask_threshold=0.0, risk_penalties=self.default_config.risk_penalties),
            "doc": ConfidenceConfig(act_threshold=0.85, ask_threshold=0.50, risk_penalties=self.default_config.risk_penalties),
            "fin": ConfidenceConfig(act_threshold=0.85, ask_threshold=0.50, risk_penalties=self.default_config.risk_penalties),
            "architect": ConfidenceConfig(act_threshold=0.75, ask_threshold=0.40, risk_penalties=self.default_config.risk_penalties),
            "sentinel": ConfidenceConfig(act_threshold=0.90, ask_threshold=0.60, risk_penalties=self.default_config.risk_penalties),
            "eva": ConfidenceConfig(act_threshold=0.80, ask_threshold=0.45, risk_penalties=self.default_config.risk_penalties),
        }
        
        self.action_risk_map = {
            "send_email": "high",
            "place_order": "critical",
            "trade_decision": "critical",
            "summarize": "low",
            "analyze": "low",
            "health_check": "low",
            "delete_data": "critical",
            "modify_config": "high",
        }

    def get_config(self, agent_id: str) -> ConfidenceConfig:
        """Return the confidence config for a given agent_id, or the default."""
        return self.agent_configs.get(agent_id.lower(), self.default_config)

    def evaluate(
        self,
        agent_id: str,
        confidence: float,
        action_type: str,
        action_risk: str = "low"
    ) -> EscalationResult:
        """
        Evaluate an action based on confidence, action type, and agent config
        to determine the required escalation level.
        """
        config = self.get_config(agent_id)
        
        derived_risk = self.action_risk_map.get(action_type, action_risk)
        penalty = config.risk_penalties.get(derived_risk, 0.0)
        
        adjusted_act_threshold = min(1.0, config.act_threshold + penalty)
        adjusted_ask_threshold = min(1.0, config.ask_threshold + penalty)
        
        level = EscalationLevel.REFUSE
        reason = "Confidence below ask threshold."
        
        if confidence >= adjusted_act_threshold:
            level = EscalationLevel.ACT
            reason = "Confidence exceeds act threshold."
        elif confidence >= adjusted_ask_threshold:
            level = EscalationLevel.ASK
            reason = "Confidence within ask threshold range."
            
        logger.info(
            "evaluated_confidence",
            agent_id=agent_id,
            action_type=action_type,
            confidence=confidence,
            level=level.name,
            derived_risk=derived_risk
        )
        
        return EscalationResult(
            level=level,
            confidence=confidence,
            adjusted_threshold=adjusted_act_threshold if level == EscalationLevel.ACT else adjusted_ask_threshold,
            reason=reason,
            action_risk=derived_risk
        )
