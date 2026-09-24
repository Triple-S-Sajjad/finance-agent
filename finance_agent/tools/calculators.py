def calculate_emi(principal: float, annual_rate_percent: float, months: int) -> dict:
    """Fixed monthly payment for an amortizing loan."""
    r = annual_rate_percent / 100 / 12   # monthly rate as a decimal
    if r == 0:
        emi = principal / months
    else:
        g = (1 + r) ** months
        emi = principal * r * g / (g - 1)

    total = emi * months
    return {
        "monthly_payment": round(emi, 2),
        "total_paid": round(total, 2),
        "total_interest": round(total - principal, 2),
    }