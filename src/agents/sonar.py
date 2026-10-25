"""Sonar Agent — Chief of Global Intelligence & Deep Research for SYNDICATE Holding."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlparse

from src.agents.director_base import DirectorAgent, number, text
from src.pii import PIIRedactor

VALID_DEPARTMENTS = {
    "eva", "architect", "marshal", "fin", "doc", "kira", "sam", "kodex",
    "alice", "oscar", "tyler", "jack", "ray", "dex", "atlas", "trainer", "scout", "andrii"
}

EVIDENCE_TIERS = {
    "Tier A": "Primary authoritative (gov, SEC, peer-reviewed, official dev docs)",
    "Tier B": "Reliable secondary (top financial press, industry publications, official blogs)",
    "Tier C": "Informational / sentiment (forums, social networks, community feedback)"
}


class SonarAgent(DirectorAgent):
    AGENT_ID = "sonar"
    ACTIONS = {
        "capabilities": "capabilities",
        "deep_research": "deep_research",
        "quick_search": "quick_search",
        "verify_sources": "verify_sources",
        "compare_entities": "compare_entities",
        "crawl_and_extract": "crawl_and_extract",
        "package_for_obsidian": "package_for_obsidian",
        "batch_plan": "batch_plan",
        "dossiers": "dossiers",
        "verifications": "verifications",
        "report": "report",
        "live_scrape": "blocked_external",
        "autonomous_crawl": "blocked_external",
    }

    def __init__(self, *args, perplexity_client=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.perplexity_client = perplexity_client
        self.redactor = PIIRedactor()

    async def deep_research(self, payload: dict) -> dict:
        topic = text(payload["topic"], "topic", 1000)
        clean_topic, _ = self.redactor.redact(topic)
        depth = text(payload.get("depth", "comprehensive"), "depth", 50).lower()
        target_wing = text(payload.get("target_wing", "eva"), "target_wing", 30).lower()
        if target_wing not in VALID_DEPARTMENTS:
            raise ValueError("unsupported_target_wing")

        # If live client provided, invoke it; otherwise generate structured analytical dossier
        engine = "sonar-deep-research" if depth == "comprehensive" else "sonar-reasoning-pro"
        
        # Zero-Faking: without a live research client or caller-supplied sources there is
        # nothing real to cite, so say so instead of inventing "internal" references.
        citations = payload.get("citations", [])
        if not isinstance(citations, list):
            raise ValueError("citations_must_be_a_list")
        if not citations and self.perplexity_client is None:
            return {
                "status": "unavailable",
                "reason": "no_research_client_and_no_sources_supplied",
                "topic": clean_topic,
                "hint": "Provide payload.citations (real sources) or configure the Perplexity client in Vault.",
            }

        if payload.get("confidence_score") is None:
            confidence, grade = None, "unrated"  # never a made-up default confidence
        else:
            confidence_val = number(payload["confidence_score"], "confidence_score", 0.0, 1.0)
            confidence = float(Decimal(str(confidence_val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            grade = "Tier A" if confidence >= 0.90 else ("Tier B" if confidence >= 0.75 else "Tier C")

        obsidian_note = (
            f"---\n"
            f"title: \"Intelligence Dossier: {clean_topic}\"\n"
            f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
            f"agent: sonar\n"
            f"target_wing: {target_wing}\n"
            f"evidence_grade: {grade}\n"
            f"confidence_score: {confidence}\n"
            f"engine: {engine}\n"
            f"tags: [intelligence, deep_research, unreviewed]\n"
            f"---\n\n"
            f"# Досьє глибинної розвідки: {clean_topic}\n\n"
            f"## 1. Статус\n"
            f"Нотатка містить лише надані джерела; висновків, не підкріплених джерелами, немає.\n\n"
            f"## 3. Першоджерела та Література\n"
            + "\n".join(f"- [{i+1}] [{c['title']}]({c['url']}) ({c['tier']}): {c['excerpt']}" for i, c in enumerate(citations))
        )

        record = self.store.add(
            "dossier",
            {
                "topic": clean_topic,
                "engine": engine,
                "depth": depth,
                "target_wing": target_wing,
                "confidence_score": confidence,
                "evidence_grade": grade,
                "citations_count": len(citations),
                "citations": citations,
                "executive_summary": None,
                "obsidian_markdown": obsidian_note,
                "state": "sources_recorded_unreviewed",
            }
        )
        return {"status": "ok", "dossier": record}

    async def quick_search(self, payload: dict) -> dict:
        query = text(payload["query"], "query", 500)
        clean_query, _ = self.redactor.redact(query)
        
        if self.perplexity_client is None:
            return {"status": "unavailable", "reason": "no_search_client_configured", "query": clean_query}
        return {"status": "unavailable", "reason": "live_search_not_wired", "query": clean_query}

    async def verify_sources(self, payload: dict) -> dict:
        claim = text(payload["claim"], "claim", 1000)
        clean_claim, _ = self.redactor.redact(claim)
        sources = payload.get("sources", [])
        if not isinstance(sources, list) or not sources:
            raise ValueError("sources_list_required")

        verified_sources = []
        for src in sources:
            url = text(src.get("url", "https://unspecified.domain"), "url", 1000)
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("invalid_source_url")
            tier = text(src.get("tier", "Tier B"), "tier", 20)
            if tier not in EVIDENCE_TIERS:
                tier = "Tier B"
            verified_sources.append({
                "url": url,
                "tier": tier,
                "status": "tier_asserted_by_caller" if tier in ("Tier A", "Tier B") else "unverified_sentiment",
                "fetched": False,
                "notes": text(src.get("notes", ""), "notes", 300)
            })

        has_authoritative = any(s["tier"] == "Tier A" for s in verified_sources)
        record = self.store.add(
            "verification",
            {
                "claim": clean_claim,
                "verified": has_authoritative or len(verified_sources) >= 2,
                "verdict": "verified_authoritative" if has_authoritative else "conditionally_supported",
                "sources_audited": len(verified_sources),
                "sources": verified_sources,
            }
        )
        return {"status": "ok", "verification": record}

    async def compare_entities(self, payload: dict) -> dict:
        criteria = payload.get("criteria", [])
        entities = payload.get("entities", [])
        if not isinstance(entities, list) or len(entities) < 2 or len(entities) > 20:
            raise ValueError("entities_list_invalid")
        if not isinstance(criteria, list) or not criteria:
            criteria = ["Reliability", "Cost", "Scalability", "API Maturity"]

        clean_entities = [text(e, "entity", 100) for e in entities]
        supplied = payload.get("scores")
        if not isinstance(supplied, dict):
            return {"status": "unavailable", "reason": "scores_required_no_invented_ratings", "entities": clean_entities}
        matrix = []
        for ent in clean_entities:
            row = supplied.get(ent)
            if not isinstance(row, dict) or any(c not in row for c in criteria):
                return {"status": "unavailable", "reason": "scores_missing_for_entity", "entity": ent}
            scores = {c: number(row[c], "score", 0, 100) for c in criteria}
            matrix.append({"entity": ent, "metrics": scores, "composite_score": round(sum(scores.values()) / len(scores), 2)})
        matrix.sort(key=lambda m: -m["composite_score"])
        clean_entities = [m["entity"] for m in matrix]

        record = self.store.add(
            "comparison",
            {
                "entities": clean_entities,
                "criteria": criteria,
                "matrix": matrix,
                "winner": clean_entities[0],
                "recommendation": f"Рекомендовано обрати '{clean_entities[0]}' на основі наданих оцінок (середній бал).",
            }
        )
        return {"status": "ok", "comparison": record}

    async def crawl_and_extract(self, payload: dict) -> dict:
        raw_url = text(payload["url"], "url", 2000)
        parsed = urlparse(raw_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("invalid_crawl_url")
        if parsed.username or parsed.password:
            raise ValueError("credentials_in_url_prohibited")

        # No network fetch happens here. Only caller-supplied page text is cleaned.
        page_text = payload.get("page_text")
        if not isinstance(page_text, str) or not page_text.strip():
            return {"status": "unavailable", "reason": "no_page_text_supplied_crawler_not_wired", "url": raw_url}
        clean_title = text(payload.get("page_title", parsed.netloc), "title", 200)
        md = f"# {clean_title}\n\n*Першоджерело: {raw_url}*\n\n{page_text.strip()[:20000]}"
        return {
            "status": "ok",
            "url": raw_url,
            "domain": parsed.netloc,
            "engine": "caller_supplied_text",
            "clean_markdown": md,
            "words_extracted": len(md.split()),
            "fetched": False,
        }

    async def package_for_obsidian(self, payload: dict) -> dict:
        record_id = text(payload["dossier_id"], "dossier_id", 100)
        dossiers = self.store.list("dossier")
        found = next((d for d in dossiers if d.get("id") == record_id), None)
        if not found:
            raise KeyError("dossier_not_found")

        export_path = f"02_Knowledge/Research/{found['topic'][:30].replace(' ', '_').lower()}.md"
        return {
            "status": "ok",
            "dossier_id": record_id,
            "export_target": "obsidian_second_brain",
            "suggested_path": export_path,
            "markdown_payload": found["obsidian_markdown"],
            "notebooklm_ready": True,
        }

    async def batch_plan(self, payload: dict) -> dict:
        days = int(number(payload.get("horizon_days", 4), "horizon_days", 3, 7))
        topics = payload.get("topics", [])
        if not isinstance(topics, list) or not topics or len(topics) > 50:
            raise ValueError("invalid_batch_topics")

        saved = []
        for item in topics:
            res = await self.deep_research({"topic": item, "depth": "balanced"})
            saved.append(res["dossier"])
        return {"status": "ok", "horizon_days": days, "planned_count": len(saved), "dossiers": saved}

    async def dossiers(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("dossier")}

    async def verifications(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("verification")}

    async def report(self, payload: dict) -> dict:
        dossiers = self.store.list("dossier")
        verifications = self.store.list("verification")
        comparisons = self.store.list("comparison")
        return {
            "status": "ok",
            "dossiers_completed": len(dossiers),
            "verifications_conducted": len(verifications),
            "comparisons_built": len(comparisons),
            "external_actions": False,
        }
