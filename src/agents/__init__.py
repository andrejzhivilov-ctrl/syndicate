"""EVA SYNDICATE Specialist Agents package."""

from src.agents.architect.agent import ArchitectAgent
from src.agents.doc import DocAgent
from src.agents.eva import EvaAgent
from src.agents.eva_curator import EvaCurator
from src.agents.fin import FinAgent
from src.agents.sam.agent import SamAgent
from src.agents.sentinel import SentinelAgent
from src.agents.office_copilot import OfficeCopilotAgent, OfficeKnowledgeBase
from src.agents.marshal import MarshalAgent
from src.agents.kira import KiraAgent

__all__ = [
    "ArchitectAgent",
    "DocAgent",
    "EvaAgent",
    "EvaCurator",
    "FinAgent",
    "SamAgent",
    "SentinelAgent",
    "OfficeCopilotAgent",
    "OfficeKnowledgeBase",
    "MarshalAgent",
    "KiraAgent",
]
