from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from services.agents.copilot_models import AgentCatalog, CopilotModelsClient, load_agent_catalog


REQUIRED_AGENTS = (
    "discovery_agent",
    "review_generation_agent",
    "media_enrichment_agent",
    "seo_optimizer_agent",
    "scoring_agent",
)


def _try_parse_json(raw_text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"raw_text": raw_text}
    return parsed if isinstance(parsed, dict) else {"raw": parsed}


def _extract_score(scoring_output: dict[str, Any]) -> float:
    parsed = _try_parse_json(str(scoring_output.get("content", "")))
    if "final_score" in parsed:
        try:
            score = float(parsed["final_score"])
            return max(0.0, min(10.0, score))
        except (TypeError, ValueError):
            return 0.0
    return 0.0


@dataclass
class ReviewOrchestrator:
    catalog: AgentCatalog
    client: CopilotModelsClient

    @classmethod
    def from_settings(cls) -> "ReviewOrchestrator":
        catalog = load_agent_catalog(settings.copilot_agent_config_path)
        client = CopilotModelsClient()
        return cls(catalog=catalog, client=client)

    def run_review(self, job_payload: dict[str, Any]) -> dict[str, Any]:
        missing_agents = [name for name in REQUIRED_AGENTS if name not in self.catalog.agents]
        if missing_agents:
            raise ValueError(f"Missing agent definitions: {', '.join(missing_agents)}")

        max_iterations = min(settings.review_max_iterations, self.catalog.review_flow.max_iterations)
        target_score = settings.review_target_score or self.catalog.review_flow.target_score

        best_score = 0.0
        best_iteration = 1
        iteration_history: list[dict[str, Any]] = []
        review_context: dict[str, Any] = {
            "request_id": job_payload["request_id"],
            "product_id": job_payload["product_id"],
            "prompt": job_payload.get("prompt", ""),
        }

        for iteration in range(1, max_iterations + 1):
            review_context["iteration"] = iteration
            review_context["context_json"] = json.dumps(review_context)

            iteration_outputs: dict[str, Any] = {}
            for agent_name in REQUIRED_AGENTS:
                agent = self.catalog.agents[agent_name]
                iteration_outputs[agent_name] = self.client.run_agent(
                    agent=agent,
                    context={
                        **review_context,
                        "model": agent.model,
                        "skills": agent.skills,
                        "mcp_servers": agent.mcp_servers,
                    },
                )

            score = _extract_score(iteration_outputs["scoring_agent"])
            if score > best_score:
                best_score = score
                best_iteration = iteration

            iteration_history.append(
                {
                    "iteration": iteration,
                    "score": score,
                    "agent_outputs": iteration_outputs,
                }
            )
            review_context["last_iteration_score"] = score
            review_context["last_iteration_summary"] = {
                "discovery": iteration_outputs["discovery_agent"]["content"],
                "review": iteration_outputs["review_generation_agent"]["content"],
                "media": iteration_outputs["media_enrichment_agent"]["content"],
                "seo": iteration_outputs["seo_optimizer_agent"]["content"],
            }

            if score >= target_score:
                break

        return {
            "request_id": job_payload["request_id"],
            "product_id": job_payload["product_id"],
            "iterations": len(iteration_history),
            "best_iteration": best_iteration,
            "score": best_score,
            "status": "pending_approval",
            "needs_human_review": best_score < target_score,
            "agent_stack": {
                name: {
                    "model": self.catalog.agents[name].model,
                    "skills": self.catalog.agents[name].skills,
                    "mcp_servers": self.catalog.agents[name].mcp_servers,
                }
                for name in REQUIRED_AGENTS
            },
            "iteration_history": iteration_history,
        }

    def run_upload_match(self, job_payload: dict[str, Any]) -> dict[str, Any]:
        discovery = self.catalog.agents.get("discovery_agent")
        if not discovery:
            raise ValueError("discovery_agent is required for upload matching")
        output = self.client.run_agent(
            agent=discovery,
            context={
                "request_id": job_payload["request_id"],
                "product_id": "unknown",
                "prompt": "Match uploaded screenshot with product catalog.",
                "iteration": 1,
                "context_json": json.dumps({"file_path": job_payload["file_path"]}),
                "model": discovery.model,
                "skills": discovery.skills,
                "mcp_servers": discovery.mcp_servers,
            },
        )
        parsed = _try_parse_json(output["content"])
        matches = parsed.get("matches") if isinstance(parsed.get("matches"), list) else []
        return {
            "request_id": job_payload["request_id"],
            "file_path": job_payload["file_path"],
            "matches": matches,
            "status": "queued_for_review" if not matches else "matched",
            "discovery_output": output,
        }
