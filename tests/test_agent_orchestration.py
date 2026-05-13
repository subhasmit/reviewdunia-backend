from services.agents.workers.review_generation_worker import generate_review, process_upload_job


def test_generate_review_uses_agent_stack():
    result = generate_review(
        {
            "request_id": "req-1",
            "product_id": 1,
            "prompt": "Generate a review for product 1",
        }
    )
    assert result["status"] == "pending_approval"
    assert "agent_stack" in result
    assert "scoring_agent" in result["agent_stack"]
    assert result["iterations"] <= 10


def test_process_upload_job_uses_discovery_agent():
    result = process_upload_job({"request_id": "req-2", "file_path": "/tmp/file.png"})
    assert result["request_id"] == "req-2"
    assert result["status"] in {"queued_for_review", "matched"}
    assert "discovery_output" in result
