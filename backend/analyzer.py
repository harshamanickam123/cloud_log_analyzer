import re
from datetime import datetime
from collections import defaultdict
import statistics


def analyze_log(content):
    lines = content.split("\n")

    errors = 0
    warnings = 0
    failed_logins = 0
    success_logins = 0
    brute_force = 0

    failed_ip_tracker = {}

    # 📈 STRONG TREND STORAGE (errors per minute)
    error_timeline = defaultdict(int)

    for line in lines:
        line_lower = line.lower()

        # ⏱️ Extract timestamp (fallback current time)
        time_match = re.search(r"\d{2}:\d{2}:\d{2}", line)
        timestamp = time_match.group() if time_match else datetime.now().strftime("%H:%M:%S")

        minute_bucket = timestamp[:5]  # HH:MM grouping

        # 🔴 ERROR DETECTION (VERY STRONG)
        if re.search(r"(error|exception|critical|fail(ed)?|crash|timeout|refused|denied|500|502|503)", line_lower):
            errors += 1
            error_timeline[minute_bucket] += 1

        # 🟠 WARNING DETECTION
        elif re.search(r"(warning|deprecated|low memory|disk almost full|retrying|slow)", line_lower):
            warnings += 1

        # 🔐 FAILED LOGIN DETECTION
        if re.search(r"(failed password|login failed|unauthorized|401|invalid user|access denied)", line_lower):
            failed_logins += 1

            ip_match = re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", line)
            if ip_match:
                ip = ip_match.group()
                failed_ip_tracker[ip] = failed_ip_tracker.get(ip, 0) + 1

        # ✅ SUCCESS LOGIN
        if re.search(r"(login success|200|logged in|accepted password|ok)", line_lower):
            success_logins += 1

    # 🚨 BRUTE FORCE DETECTION
    for ip, count in failed_ip_tracker.items():
        if count >= 3:
            brute_force += 1

    # 📈 TREND DATA PREPARE
    trend_data = []
    error_values = []

    for time in sorted(error_timeline.keys()):
        count = error_timeline[time]
        trend_data.append({
            "time": time,
            "errors": count
        })
        error_values.append(count)

    # 🚨🔥 STRONG ANOMALY DETECTION (Z-SCORE + SPIKE)
    anomaly = False
    anomaly_reason = ""

    if len(error_values) >= 3:
        mean = statistics.mean(error_values)
        std_dev = statistics.stdev(error_values) if len(error_values) > 1 else 0
        latest = error_values[-1]

        # Z-SCORE METHOD
        if std_dev > 0:
            z_score = (latest - mean) / std_dev

            if z_score > 2:
                anomaly = True
                anomaly_reason = f"Abnormal spike detected (Z-score: {round(z_score,2)})"

        # 🔥 EXTRA SPIKE CHECK (more real-world)
        if len(error_values) >= 2:
            prev = error_values[-2]

            if prev > 0 and latest >= prev * 2:
                anomaly = True
                anomaly_reason = "Sudden spike: errors doubled compared to previous interval"

    # 📊 RISK SCORE
    risk_score = (errors * 5) + (warnings * 2) + (failed_logins * 4)

    if risk_score > 50:
        risk_level = "HIGH 🔴"
        severity_msg = "Critical system risk detected!"
    elif risk_score > 20:
        risk_level = "MEDIUM 🟠"
        severity_msg = "Moderate issues found, needs attention."
    else:
        risk_level = "LOW 🟢"
        severity_msg = "System is mostly stable."

    # 🧠 AI STYLE EXPLANATION
    explanation = f"""
🔍 AI LOG ANALYSIS REPORT

📊 Summary:
- Total ERROR events: {errors}
- Total WARNING events: {warnings}
- Failed login attempts: {failed_logins}
- Successful logins: {success_logins}

⚠️ Risk Evaluation:
{severity_msg}

📈 Trend Insight:
- Errors are distributed across time intervals for behavior tracking

🚨 Anomaly Detection:
{anomaly_reason if anomaly else 'No statistical anomaly detected'}

🧠 Root Cause Analysis:
- Errors indicate crashes, HTTP failures, or backend issues.
- Warnings indicate performance or resource problems.
- Failed logins suggest unauthorized access attempts.

🔐 Security Insight:
- Multiple failures from same IP → brute-force attack
- Sudden error spike → system instability or attack

💡 Recommendations:
- Investigate sudden spikes immediately
- Monitor logs continuously
- Block suspicious IPs
- Fix recurring backend errors
- Enable alerting systems

📈 Final Risk Score: {risk_score} ({risk_level})
"""

    return {
        "errors": errors,
        "warnings": warnings,
        "failed_logins": failed_logins,
        "success_logins": success_logins,
        "bruteforce": brute_force,
        "trend": trend_data,
        "anomaly": anomaly,
        "anomaly_reason": anomaly_reason,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation
    }