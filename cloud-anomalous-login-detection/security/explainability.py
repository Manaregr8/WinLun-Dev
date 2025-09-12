def explain_result(result: dict) -> str:
    """
    Turn evaluation result into a human-readable explanation.
    """
    score = result["risk_score"]
    reasons = result["reasons"]

    if "No anomalies detected" in reasons:
        return f"✅ Login is SAFE (score {score})"

    explanation = f"⚠️ Suspicious Login (score {score})\nReasons:"
    for r in reasons:
        explanation += f"\n - {r}"
    return explanation
