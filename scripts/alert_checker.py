import json
import os
import requests

# --------------------------------------------------
# File paths
# --------------------------------------------------

HEALTH_REPORT = "data/processed/health_report.json"
ALERT_LOG = "data/raw/alerts.log"
STATE_FILE = "data/processed/alert_state.json"
WEBHOOK_URL = "http://127.0.0.1:5001/webhook"


# --------------------------------------------------
# Load health report
# --------------------------------------------------

with open(
    HEALTH_REPORT,
    "r",
    encoding="utf-8"
) as file:

    health_report = json.load(file)


# --------------------------------------------------
# Load previous alert state
# --------------------------------------------------

if os.path.exists(STATE_FILE):

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        previous_state = json.load(file)

else:

    previous_state = {
        "memory": "OK",
        "disk": "OK",
        "cpu": "OK"
    }


# --------------------------------------------------
# Get latest health record
# --------------------------------------------------

if not health_report:

    print("No health data available.")
    exit()


latest_record = health_report[-1]

date = latest_record["date"]
status = latest_record["status"]


current_state = {
    "memory": status["memory"]["status"],
    "disk": status["disk"]["status"],
    "cpu": status["cpu"]["status"]
}


# --------------------------------------------------
# Detect new problems and recoveries
# --------------------------------------------------

events = []


for metric in ["memory", "disk", "cpu"]:

    old_status = previous_state.get(metric, "OK")
    new_status = current_state[metric]

    usage = status[metric]["usage_percent"]


    # New WARNING or CRITICAL condition
    if (
        new_status in ["WARNING", "CRITICAL"]
        and old_status == "OK"
    ):

        events.append(
            f"ALERT: {metric.upper()} usage is "
            f"{usage}% [{new_status}]"
        )


    # Escalation from WARNING to CRITICAL
    elif (
        old_status == "WARNING"
        and new_status == "CRITICAL"
    ):

        events.append(
            f"ALERT: {metric.upper()} usage escalated "
            f"to {usage}% [CRITICAL]"
        )


    # Recovery
    elif (
        old_status in ["WARNING", "CRITICAL"]
        and new_status == "OK"
    ):

        events.append(
            f"RECOVERY: {metric.upper()} usage returned "
            f"to {usage}% [OK]"
        )


# --------------------------------------------------
# Write events
# --------------------------------------------------

# --------------------------------------------------
# Send notifications
# --------------------------------------------------

if events:

    with open(
        ALERT_LOG,
        "a",
        encoding="utf-8"
    ) as alert_file:

        alert_file.write(
            f"\n[{date}]\n"
        )

        for event in events:

            alert_file.write(
                f"{event}\n"
            )

    for event in events:

        print(event)

        payload = {
            "alert": event,
            "date": date
        }

        try:

            response = requests.post(
                WEBHOOK_URL,
                json=payload,
                timeout=5
            )

            if response.status_code == 200:

                print("Webhook notification sent.")

            else:

                print(
                    f"Webhook failed with status "
                    f"{response.status_code}"
                )

        except requests.RequestException as error:

            print(
                f"Webhook notification failed: {error}"
            )

else:

    print("No new alerts or recoveries.")


# --------------------------------------------------
# Save current state
# --------------------------------------------------

with open(
    STATE_FILE,
    "w",
    encoding="utf-8"
) as state_file:

    json.dump(
        current_state,
        state_file,
        indent=4
    )