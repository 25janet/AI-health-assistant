import os
import json

from dotenv import load_dotenv
from google import genai


# ------------------------------------------------------------
# 1. Load environment variables
# ------------------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")


# ------------------------------------------------------------
# 2. Create Gemini client
# ------------------------------------------------------------

client = genai.Client(api_key=api_key)


# ------------------------------------------------------------
# 3. Load health report
# ------------------------------------------------------------

with open(
    "data/processed/health_report.json",
    "r",
    encoding="utf-8"
) as file:

    health_report = json.load(file)


# ------------------------------------------------------------
# 4. Load alert log
# ------------------------------------------------------------

if os.path.exists("data/raw/alerts.log"):

    with open(
        "data/raw/alerts.log",
        "r",
        encoding="utf-8"
    ) as file:

        alerts = file.read()

else:

    alerts = "No alerts recorded."


# ------------------------------------------------------------
# 5. Get the latest health record
# ------------------------------------------------------------

latest_record = health_report[-1]

health_data = json.dumps(
    latest_record,
    indent=4
)


# ------------------------------------------------------------
# 6. Create AI explanation prompt
# ------------------------------------------------------------

prompt = f"""
You are an AI Linux Health Assistant.

A local monitoring system has detected a health event.

Your job is to explain what the monitoring data shows.

LATEST HEALTH RECORD
====================

{health_data}


ALERT HISTORY
=============

{alerts}


RULES
=====

1. Base your explanation only on the provided data.

2. Clearly identify the affected resource:
   CPU, memory, disk, or another recorded metric.

3. Mention the recorded usage percentage and status.

4. If process information is available, use it as
   supporting evidence.

5. Do not claim that a process caused the problem unless
   the available data proves this.

6. Clearly distinguish:
   - what the monitoring data directly shows
   - what can reasonably be inferred
   - possible explanations that are not confirmed.

7. If there is insufficient information to determine
   the cause, say so.

8. Explain the situation in beginner-friendly language.

9. Keep the explanation concise and practical.

10. Do not use medical-style statements such as
    "nothing to worry about."

Provide:

- What happened
- What the data shows
- Possible explanation
- What should be checked next
"""


# ------------------------------------------------------------
# 7. Ask Gemini for an explanation
# ------------------------------------------------------------

interaction = client.interactions.create(
    model=model,
    input=prompt
)


# ------------------------------------------------------------
# 8. Display the explanation
# ------------------------------------------------------------

print("\n========================================")
print("       AI ALERT EXPLANATION")
print("========================================\n")

print(interaction.output_text)