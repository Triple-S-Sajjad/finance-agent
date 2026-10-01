from finance_agent.tools import run_tool


def test_unknown_tool_returns_error():
    r = run_tool("delete_everything", {})
    assert "unknown tool" in r["error"]


def test_bad_args_return_error_not_crash():
    r = run_tool("calculate_emi", {"principal": 1})
    assert "missing" in r["error"]