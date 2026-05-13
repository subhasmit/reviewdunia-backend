from __future__ import annotations

from typing import Any

from services.agents.orchestrator import ReviewOrchestrator


def generate_review(job_payload: dict[str, Any]) -> dict[str, Any]:
    orchestrator = ReviewOrchestrator.from_settings()
    return orchestrator.run_review(job_payload)


def process_upload_job(job_payload: dict[str, Any]) -> dict[str, Any]:
    orchestrator = ReviewOrchestrator.from_settings()
    return orchestrator.run_upload_match(job_payload)
