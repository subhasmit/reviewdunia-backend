from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    model: str
    system_prompt: str
    prompt_template: str
    skills: list[str]
    mcp_servers: list[str]


@dataclass(frozen=True)
class ReviewFlowConfig:
    max_iterations: int
    target_score: float


@dataclass(frozen=True)
class AgentCatalog:
    review_flow: ReviewFlowConfig
    agents: dict[str, AgentDefinition]


def _render_template(template: str, values: dict[str, Any]) -> str:
    normalized = template.replace("{{", "${").replace("}}", "}")
    return Template(normalized).safe_substitute(**values)


def load_agent_catalog(config_path: str | None = None) -> AgentCatalog:
    resolved = Path(config_path or settings.copilot_agent_config_path)
    raw = json.loads(resolved.read_text(encoding="utf-8"))

    review_flow = ReviewFlowConfig(
        max_iterations=int(raw["review_flow"]["max_iterations"]),
        target_score=float(raw["review_flow"]["target_score"]),
    )
    agents: dict[str, AgentDefinition] = {}
    for name, data in raw["agents"].items():
        agents[name] = AgentDefinition(
            name=name,
            model=data["model"],
            system_prompt=data["system_prompt"],
            prompt_template=data["prompt_template"],
            skills=list(data.get("skills", [])),
            mcp_servers=list(data.get("mcp_servers", [])),
        )
    return AgentCatalog(review_flow=review_flow, agents=agents)


class CopilotModelsClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
        dry_run: bool | None = None,
    ) -> None:
        self.api_key = api_key or settings.copilot_models_api_key
        self.base_url = (base_url or settings.copilot_models_api_base_url).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.copilot_request_timeout_seconds
        self.dry_run = settings.copilot_dry_run if dry_run is None else dry_run

    def run_agent(self, agent: AgentDefinition, context: dict[str, Any]) -> dict[str, Any]:
        prompt = _render_template(agent.prompt_template, context)
        if self.dry_run:
            return self._mock_response(agent.name, context)
        if not self.api_key:
            raise RuntimeError("COPILOT_MODELS_API_KEY is required when copilot_dry_run is false")

        payload = {
            "model": agent.model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": agent.system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            "metadata": {
                "agent_name": agent.name,
                "skills": agent.skills,
                "mcp_servers": agent.mcp_servers,
            },
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(f"{self.base_url}/responses", json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
        return {
            "model": agent.model,
            "skills": agent.skills,
            "mcp_servers": agent.mcp_servers,
            "content": self._extract_text_content(body),
            "raw": body,
        }

    def _extract_text_content(self, body: dict[str, Any]) -> str:
        if isinstance(body.get("output_text"), str):
            return body["output_text"]
        output = body.get("output", [])
        if not isinstance(output, list):
            return json.dumps(body)
        parts: list[str] = []
        for item in output:
            content = item.get("content", []) if isinstance(item, dict) else []
            for chunk in content:
                text = chunk.get("text") if isinstance(chunk, dict) else None
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts) if parts else json.dumps(body)

    def _mock_response(self, agent_name: str, context: dict[str, Any]) -> dict[str, Any]:
        iteration = int(context.get("iteration", 1))
        if agent_name == "scoring_agent":
            score = min(10.0, round(8.2 + (iteration * 0.2), 2))
            content = json.dumps(
                {
                    "rubric": {
                        "accuracy": min(10.0, score + 0.1),
                        "completeness": score,
                        "media_quality": max(0.0, score - 0.2),
                        "readability": score,
                        "seo_optimization": min(10.0, score + 0.2),
                        "originality": max(0.0, score - 0.1),
                    },
                    "final_score": score,
                    "notes": "Mock scoring response.",
                }
            )
        else:
            content = json.dumps(
                {
                    "agent": agent_name,
                    "iteration": iteration,
                    "summary": "Mock agent execution.",
                }
            )
        return {
            "model": context.get("model", "dry-run"),
            "skills": context.get("skills", []),
            "mcp_servers": context.get("mcp_servers", []),
            "content": content,
            "raw": {"dry_run": True},
        }
