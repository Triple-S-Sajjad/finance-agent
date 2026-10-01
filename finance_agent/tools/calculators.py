class ToolArgError(ValueError):
    """Bad arguments from the model. The message is sent back so it can retry."""


def _num(args: dict, key: str, lo: float, hi: float, integer: bool = False):
    if key not in args:
        raise ToolArgError(f"missing required argument '{key}'")
    raw = args[key]
    if isinstance(raw, str):  # tolerate "20,000", "$500", "7%"
        raw = raw.replace(",", "").replace("$", "").replace("%", "").strip()
    try:
        val = float(raw)
    except (TypeError, ValueError):
        raise ToolArgError(f"'{key}' must be a number, got {args[key]!r}")
    if integer:
        if not val.is_integer():
            raise ToolArgError(f"'{key}' must be a whole number, got {val}")
        val = int(val)
    if not lo <= val <= hi:
        raise ToolArgError(f"'{key}' must be between {lo} and {hi}, got {val}")
    return val


def calculate_emi(args: dict) -> dict:
    """Fixed monthly payment for an amortizing loan."""
    principal = _num(args, "principal", 1, 1e9)
    rate = _num(args, "annual_rate_percent", 0, 100)
    months = _num(args, "months", 1, 600, integer=True)

    r = rate / 100 / 12
    if r == 0:
        emi = principal / months
    else:
        g = (1 + r) ** months
        emi = principal * r * g / (g - 1)

    total = emi * months
    return {
        "currency": "USD",
        "monthly_payment": round(emi, 2),
        "total_paid": round(total, 2),
        "total_interest": round(total - principal, 2),
    }


EMI_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate_emi",
        "description": "Calculate the fixed monthly payment (EMI), total paid, and total "
                       "interest for a loan. Use for any loan, mortgage, or financing payment question.",
        "parameters": {
            "type": "object",
            "properties": {
                "principal": {"type": "number", "description": "Loan amount, e.g. 20000"},
                "annual_rate_percent": {"type": "number", "description": "Annual interest rate in percent, e.g. 7 for 7%"},
                "months": {"type": "integer", "description": "Loan term in months. Convert years to months (5 years = 60)."},
            },
            "required": ["principal", "annual_rate_percent", "months"],
        },
    },
}