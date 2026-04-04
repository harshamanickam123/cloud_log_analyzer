def analyze_log(content):
    errors = content.count("ERROR")
    warnings = content.count("WARNING")
    failed_logins = content.count("Failed")
    success_logins = content.count("Success")

    # Risk Score Calculation
    risk_score = (errors * 5) + (warnings * 2) + (failed_logins * 4)

    # Risk Level + Color Tag
    if risk_score > 50:
        risk_level = "HIGH 🔴"
        severity_msg = "Critical system risk detected!"
    elif risk_score > 20:
        risk_level = "MEDIUM 🟠"
        severity_msg = "Moderate issues found, needs attention."
    else:
        risk_level = "LOW 🟢"
        severity_msg = "System is mostly stable."

    # AI STYLE EXPLANATION (SMART)
    explanation = f"""
🔍 AI LOG ANALYSIS REPORT

📊 Summary:
- Total ERROR events: {errors}
- Total WARNING events: {warnings}
- Failed login attempts: {failed_logins}
- Successful logins: {success_logins}

⚠️ Risk Evaluation:
{severity_msg}

🧠 Root Cause Analysis:
- High ERROR count indicates possible system crashes or misconfigurations.
- WARNING messages suggest potential future failures.
- Failed logins may indicate brute-force or unauthorized access attempts.

🔐 Security Insight:
- If failed logins are high → possible attack attempt.
- If errors are high → backend/service instability.

💡 Recommendations:
- Monitor server logs continuously
- Enable firewall / authentication protection
- Fix repeated ERROR sources immediately
- Consider alert systems for unusual activity

📈 Final Risk Score: {risk_score} ({risk_level})
"""

    return {
        "errors": errors,
        "warnings": warnings,
        "failed_logins": failed_logins,
        "success_logins": success_logins,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation
    }