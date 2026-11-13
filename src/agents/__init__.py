"""SYNDICATE specialists, loaded on demand for isolated workers."""
from importlib import import_module

_EXPORTS = {
    "DocAgent": "src.agents.alex.doc",
    "EvaAgent": "src.agents.eva",
    "EvaCurator": "src.agents.eva_curator",
    "FinAgent": "src.agents.fin",
    "SamAgent": "src.agents.sam.agent",
    "SentinelAgent": "src.agents.sentinel",
    "OfficeCopilotAgent": "src.agents.office_copilot",
    "OfficeKnowledgeBase": "src.agents.office_copilot",
    "MarshalAgent": "src.agents.marshal",
    "KiraAgent": "src.agents.kira",
    "OscarAgent": "src.agents.tyler.oscar",
    "TylerAgent": "src.agents.tyler",
    "JackAgent": "src.agents.sam.jack",
    "TrainerAgent": "src.agents.alex.trainer",
    "KodexAgent": "src.agents.eva_kodex",
}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value
