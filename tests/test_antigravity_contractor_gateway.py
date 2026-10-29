"""
Unit tests for Universal Antigravity Super-Agent Contractor Gateway.
Validates isolated channels, interactive dialogue, rolling memory compaction, and cryptographic signing.
"""

from __future__ import annotations

from pathlib import Path


from src.integrations.antigravity_contractor_gateway import (
    AntigravityContractorGateway,
)


def test_isolated_channels_per_agent(tmp_path: Path):
    gateway = AntigravityContractorGateway(channels_dir=tmp_path / "channels")

    # Oscar opens a task
    oscar_res = gateway.agent_submits_task(
        agent_id="oscar",
        task_title="Build 3D Landing Page",
        task_prompt="Create interactive React / Tailwind landing page with APEX-UI theme.",
    )
    assert oscar_res["status"] == "task_opened"
    assert oscar_res["channel_id"] == "channel-oscar"

    # Jack opens a task
    jack_res = gateway.agent_submits_task(
        agent_id="jack",
        task_title="PariMatch +EV Scanner",
        task_prompt="Parse Premier League odds and detect value bet anomalies.",
    )
    assert jack_res["status"] == "task_opened"
    assert jack_res["channel_id"] == "channel-jack"

    # Check channels are isolated
    oscar_channel = gateway.get_channel("oscar")
    jack_channel = gateway.get_channel("jack")

    oscar_msgs = oscar_channel.get_messages()
    jack_msgs = jack_channel.get_messages()

    assert len(oscar_msgs) == 1
    assert "3D Landing Page" in oscar_msgs[0].content
    assert len(jack_msgs) == 1
    assert "PariMatch" in jack_msgs[0].content
    assert "PariMatch" not in oscar_msgs[0].content


def test_interactive_dialogue_and_delivery(tmp_path: Path):
    gateway = AntigravityContractorGateway(channels_dir=tmp_path / "channels")

    # 1. Oscar submits task
    gateway.agent_submits_task(
        agent_id="oscar",
        task_title="Creative Website",
        task_prompt="Need site for product launch.",
    )

    # 2. Oscar replies with clarifications
    reply_res = gateway.agent_sends_reply(
        agent_id="oscar",
        message="Use Cyan + Obsidian palette, include pulsating orb component.",
    )
    assert reply_res["status"] == "sent"

    # 3. Antigravity delivers completed, tested work
    delivery_res = gateway.antigravity_delivers_work(
        agent_id="oscar",
        deliverable_summary="Fully assembled React landing page with 3D Canvas orb.",
        instructions="Run `npm install && npm run build`. Dist folder is ready for deploy.",
        files={"LandingPage.tsx": "...", "OrbCore.tsx": "..."},
    )
    assert delivery_res["status"] == "delivered"
    assert delivery_res["files_count"] == 2

    # Check full conversation history in Oscar's channel
    channel = gateway.get_channel("oscar")
    messages = channel.get_messages()
    assert len(messages) == 3
    assert messages[-1].sender == "contractor:antigravity"
    assert "РОБОТУ ВИКОНАНО ТА ПРОТЕСТОВАНО" in messages[-1].content


def test_rolling_memory_compaction(tmp_path: Path):
    gateway = AntigravityContractorGateway(channels_dir=tmp_path / "channels")
    channel = gateway.get_channel("architect")

    # Fill channel with 30 messages to trigger rolling compaction
    for i in range(30):
        channel.append_message(
            sender="agent:architect" if i % 2 == 0 else "contractor:antigravity",
            content=f"Iterative message step #{i}: refactoring microservice architecture.",
            stage="in_development",
        )

    # Check that compaction occurred
    checkpoints = list(channel.checkpoints_dir.glob("*.md"))
    assert len(checkpoints) >= 1

    active_msgs = channel.get_messages()
    assert len(active_msgs) < 30
    assert len(active_msgs) == 10  # 5 retained from compaction + 5 appended after


def test_gateway_signature_verification(tmp_path: Path):
    gateway = AntigravityContractorGateway(
        channels_dir=tmp_path / "channels",
        secret_key="top-secret-gateway-key-2026",
    )
    payload = {
        "channel_id": "channel-fin",
        "action": "crypto_risk_model",
        "timestamp": "2026-10-22T11:00:00Z",
    }
    sig = gateway.compute_signature(payload)
    payload["signature"] = sig

    assert gateway.verify_signature(payload) is True

    # Tampering test
    tampered = dict(payload)
    tampered["action"] = "tampered_action"
    assert gateway.verify_signature(tampered) is False
