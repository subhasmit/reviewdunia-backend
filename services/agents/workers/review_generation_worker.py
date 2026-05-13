from __future__ import annotations

import random
from typing import Any


def scoring_function(iteration: int, prompt: str | None = None) -> float:
    base = 0.55 + (iteration * 0.04)
    prompt_bonus = min(len(prompt or "") / 1000, 0.05)
    noise = random.uniform(-0.02, 0.02)
    return round(max(0.0, min(1.0, base + prompt_bonus + noise)), 4)


def generate_review(job_payload: dict[str, Any]) -> dict[str, Any]:
    max_iterations = 10
    best_score = 0.0
    best_iteration = 1

    for iteration in range(1, max_iterations + 1):
        score = scoring_function(iteration, job_payload.get("prompt"))
        if score > best_score:
            best_score = score
            best_iteration = iteration

    return {
        "request_id": job_payload["request_id"],
        "product_id": job_payload["product_id"],
        "iterations": max_iterations,
        "best_iteration": best_iteration,
        "score": best_score,
        "status": "pending_approval",
    }


def process_upload_job(job_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": job_payload["request_id"],
        "file_path": job_payload["file_path"],
        "matches": [],
        "status": "queued_for_review",
    }
