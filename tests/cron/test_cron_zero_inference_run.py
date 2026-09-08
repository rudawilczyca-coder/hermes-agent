"""Behavioral coverage for false-success zero-inference cron runs (#100180)."""

from unittest.mock import MagicMock, patch

from cron.scheduler import run_job


def _run_with_result(result, tmp_path):
    job = {
        "id": "zero-inference-test",
        "name": "zero inference test",
        "prompt": "perform scheduled work",
        "model": "test-model",
        "provider": "openrouter",
        "provider_snapshot": None,
        "base_url": None,
    }
    fake_db = MagicMock()
    with (
        patch("cron.scheduler._hermes_home", tmp_path),
        patch("cron.scheduler_delivery._resolve_origin", return_value=None),
        patch("hermes_cli.env_loader.load_hermes_dotenv"),
        patch("hermes_cli.env_loader.reset_secret_source_cache"),
        patch("hermes_state_registry.acquire", return_value=fake_db),
        patch(
            "hermes_cli.runtime_provider.resolve_runtime_provider",
            return_value={
                "api_key": "test-key",
                "base_url": "https://example.invalid/v1",
                "provider": "openrouter",
                "api_mode": "chat_completions",
            },
        ),
        patch("run_agent.AIAgent") as agent_cls,
    ):
        agent = MagicMock()
        agent.run_conversation.return_value = result
        agent_cls.return_value = agent
        return run_job(job)


def test_run_job_fails_when_agent_reports_zero_inference_calls(tmp_path):
    success, output, final_response, error = _run_with_result(
        {
            "final_response": "Starting maintenance. Step one —",
            "api_calls": 0,
            "completed": True,
            "failed": False,
        },
        tmp_path,
    )

    assert success is False
    assert final_response == ""
    assert error is not None
    assert "zero inference calls" in error.lower()
    assert "FAILED" in output


def test_run_job_accepts_silent_result_after_a_real_inference_call(tmp_path):
    success, _output, final_response, error = _run_with_result(
        {"final_response": "", "api_calls": 1, "completed": True, "failed": False},
        tmp_path,
    )

    assert success is True
    assert final_response == ""
    assert error is None


def test_run_job_keeps_backward_compatibility_for_missing_call_count(tmp_path):
    success, _output, final_response, error = _run_with_result(
        {"final_response": "legacy result", "completed": True, "failed": False},
        tmp_path,
    )

    assert success is True
    assert final_response == "legacy result"
    assert error is None
