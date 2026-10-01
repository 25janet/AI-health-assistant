# ============================================================
# AI Linux Health Assistant - Health Report Analysis
# ============================================================

# 1. Import required libraries
import os
import json

from dotenv import load_dotenv
from google import genai


# 2. Load variables from the .env file
load_dotenv()


# 3. Get Gemini configuration from environment variables
model = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")


# 4. Create the Gemini client
client = genai.Client(api_key=api_key)


# 5. Read the health report from the JSON file
with open("json/health_report.json", "r", encoding="utf-8") as file:

    # Convert JSON data into Python data
    health_report = json.load(file)


# 6. Convert the Python health report into text
#    so we can include it in our prompt.
health_report_text = json.dumps(health_report, indent=4)


# 7. Create the prompt for Gemini
prompt = f"""
You are a Linux system health assistant.

Analyze the following Linux health monitoring report.

Health Report:
{health_report_text}

Please provide:

1. The overall health of the system.
2. Any concerning CPU, memory, or disk readings.
3. What those readings could mean.
4. Recommended actions for the system administrator.

Keep the explanation clear and beginner-friendly.
"""


# 8. Send the health report to Gemini
interaction = client.interactions.create(
    model=model,
    input=prompt
)


# 9. Display Gemini's analysis
print("\n========== AI HEALTH ANALYSIS ==========\n")
print(interaction.output_text)