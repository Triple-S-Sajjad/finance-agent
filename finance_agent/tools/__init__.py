from finance_agent.tools.calculators import EMI_SCHEMA, ToolArgError, calculate_emi

# name -> (function, schema). Every new tool gets one line here.
REGISTRY = {
    "calculate_emi": (calculate_emi, EMI_SCHEMA),
}


def schemas() -> list[dict]:
    return [schema for _, schema in REGISTRY.values()]


def run_tool(name: str, args: dict) -> dict:
    """Run a tool. Never raises: errors go back to the model as data."""
    if name not in REGISTRY:
        return {"error": f"unknown tool '{name}'. Available: {list(REGISTRY)}"}
    fn, _ = REGISTRY[name]
    try:
        return fn(args)
    except ToolArgError as e:
        return {"error": str(e)}