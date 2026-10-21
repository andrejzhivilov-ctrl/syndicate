"""
Tests for TrainerAgent (Coach) — SYNDICATE Autonomous Holding.
Physical Performance, Workouts, Nutrition, Recipes, Shopping Lists, and Self-Improvement.
"""

from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest

from src.agents.doc import DocAgent
from src.agents.trainer import TrainerAgent


class MockMemory:
    def __init__(self) -> None:
        self.saved_episodes: List[Dict[str, Any]] = []

    async def save_episode(self, **kwargs) -> None:
        self.saved_episodes.append(kwargs)

    async def recall_semantic(self, **kwargs) -> List[Dict[str, Any]]:
        return []

    async def get_recent_episodes(self, **kwargs) -> List[Dict[str, Any]]:
        return []


class MockLLM:
    def __init__(self, response_text: str = "Expert coaching recommendation.") -> None:
        self.response_text = response_text

    async def ainvoke(self, messages) -> Any:
        class _Resp:
            def __init__(self, c: str) -> None:
                self.content = c

        return _Resp(self.response_text)


def run_async(coro):
    return asyncio.run(coro)


def test_trainer_agent_init():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)
    assert agent.AGENT_ID == "trainer"
    assert "workout_plan" in agent._ACTION_MAP
    assert "nutrition_plan" in agent._ACTION_MAP
    assert "training_protocol" in agent._ACTION_MAP


def test_trainer_training_protocol_with_score():
    memory = MockMemory()
    llm = MockLLM("Warm up well and execute main lifts with strict form.")
    agent = TrainerAgent(memory=memory, llm=llm)

    res = run_async(agent.execute({
        "action": "training_protocol",
        "readiness_score": 85.0,
        "training_type": "strength",
        "goal": "hypertrophy",
        "equipment_available": ["barbell", "dumbbells"],
    }))

    assert res["status"] == "ok"
    assert res["intensity"] == "high"
    assert res["duration_min"] == 60
    assert "workout" in res
    assert len(res["workout"]["main_block"]) > 0
    assert res["equipment_available"] == ["barbell", "dumbbells"]


def test_trainer_training_protocol_missing_score_returns_unavailable():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "training_protocol",
        # No readiness_score provided
    }))

    assert res["status"] == "unavailable"
    assert res["workout"] is None
    assert "readiness_score not supplied" in res["warning"]


def test_trainer_workout_plan_search():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "workout_plan",
        "muscle": "abdominals",
        "level": "beginner",
    }))

    assert res["status"] == "ok"
    assert res["muscle"] == "abdominals"
    assert res["exercises_count"] > 0
    assert all(e["level"] == "beginner" for e in res["exercises"])


def test_trainer_exercise_search():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "exercise_search",
        "muscle": "biceps",
        "limit": 3,
    }))

    assert res["status"] == "ok"
    assert 0 < res["count"] <= 3


def test_trainer_nutrition_plan_mifflin_st_jeor():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    # 80 kg, 180 cm, 30 y, male, moderate activity
    # BMR = 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    # TDEE = 1780 * 1.55 = 2759
    res = run_async(agent.execute({
        "action": "nutrition_plan",
        "weight_kg": 80,
        "height_cm": 180,
        "age": 30,
        "sex": "male",
        "activity_level": "moderate",
        "goal": "maintenance",
    }))

    assert res["status"] == "ok"
    assert res["calories"] == 2759
    assert res["protein_g"] == 160  # 80 * 2.0
    assert res["fat_g"] == 80       # 80 * 1.0
    assert res["water_ml"] == 2800  # 80 * 35.0


def test_trainer_nutrition_plan_missing_metrics_returns_unavailable():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "nutrition_plan",
        "weight_kg": 80,
        # missing height_cm, age, sex, activity_level
    }))

    assert res["status"] == "unavailable"
    assert res["calories"] is None
    assert "height_cm" in res["missing_inputs"]


def test_trainer_recipe_plan():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "recipe_plan",
        "calories": 2500,
        "protein_g": 160,
    }))

    assert res["status"] == "ok"
    assert len(res["recipes"]) > 0
    assert "ingredients" in res["recipes"][0]


def test_trainer_shopping_list_normalization():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    # Passing raw string list
    res = run_async(agent.execute({
        "action": "shopping_list",
        "items": ["chicken", "rice"],
    }))

    assert res["status"] in ("ok", "ready_for_eva")
    assert res["from"] == "doc"  # standard basket contract from doc_shopping
    assert len(res["items"]) == 2


def test_trainer_supplement_protocol():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "supplement_protocol",
        "goal": "strength",
    }))

    assert res["status"] == "ok"
    assert len(res["protocol"]) >= 3
    assert any("Креатин" in s["name"] for s in res["protocol"])


def test_trainer_habit_tracker():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "habit_tracker",
        "habits": [
            {"name": "hydration_2.5L", "completed": True},
            {"name": "steps_8000", "completed": True},
            {"name": "screen_off_2200", "completed": False},
        ],
    }))

    assert res["status"] == "ok"
    assert res["completed_count"] == 2
    assert res["total_habits"] == 3
    assert res["completion_rate_pct"] == 66.7


def test_trainer_active_recovery():
    memory = MockMemory()
    agent = TrainerAgent(memory=memory)

    res = run_async(agent.execute({
        "action": "active_recovery",
        "fatigue_level": "high",
    }))

    assert res["status"] == "ok"
    assert res["intensity"] == "very_low"
    assert "contrast_shower" in res["modalities"]


def test_doc_delegates_training_and_nutrition_to_trainer():
    memory = MockMemory()
    doc = DocAgent(memory=memory)

    # Calling training_protocol on Doc
    res_tp = run_async(doc.execute({
        "action": "training_protocol",
        "readiness_score": 75,
    }))
    assert res_tp["delegated_by"] == "doc"
    assert res_tp["agent"] == "trainer"
    assert res_tp["status"] == "ok"

    # Calling nutrition_plan on Doc
    res_np = run_async(doc.execute({
        "action": "nutrition_plan",
        "weight_kg": 75,
        "height_cm": 175,
        "age": 28,
        "sex": "female",
        "activity_level": "light",
    }))
    assert res_np["delegated_by"] == "doc"
    assert res_np["agent"] == "trainer"
    assert res_np["status"] == "ok"
