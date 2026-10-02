# ============================================================
# AI Linux Health Assistant
# ============================================================

# Import the libraries we need
import os
import json

from dotenv import load_dotenv
from google import genai


# ------------------------------------------------------------
# 1. Load environment variables from .env
# ------------------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")


# ------------------------------------------------------------
# 2. Create the Gemini client
# ------------------------------------------------------------

client = genai.Client(api_key=api_key)


# ------------------------------------------------------------
# 3. Load the Linux health report
# ------------------------------------------------------------

with open("data/processed/health_report.json", "r", encoding="utf-8") as file:
    health_report = json.load(file)


# Convert the Python data into readable JSON text
health_report_text = json.dumps(health_report, indent=4)


# ------------------------------------------------------------
# 4. Display the assistant
# ------------------------------------------------------------

print("\n========================================")
print("       AI LINUX HEALTH ASSISTANT")
print("========================================")
print("Ask questions about your Linux system.")
print("Type 'exit' to quit.\n")


# ------------------------------------------------------------
# 5. Start the conversation loop
# ------------------------------------------------------------

while True:

    # Ask the user for a question
    user_question = input("You: ")

    # Stop the program if the user types exit
    if user_question.lower() == "exit":
        print("\nGoodbye!")
        break

    # --------------------------------------------------------
    # 6. Create the prompt
    # --------------------------------------------------------

    prompt = f"""
You are an AI Linux Health Assistant.

Your job is to help the user understand the health
and performance of their Linux system using the
provided health monitoring history.

The health report contains multiple health-check records.
Each record contains:

- date: when the health check was performed
- memory: memory usage percentage and recorded status
- disk: disk usage percentage and recorded status
- cpu: CPU usage percentage and recorded status

Below is the Linux health monitoring history:

{health_report_text}

The user has asked:

{user_question}

Use the health history to answer the question.

Rules:

1. Base your answer only on information contained
   in the health report.

2. When useful, compare older and newer health-check
   records to identify changes or trends.

3. Distinguish between:
   - a one-time spike
   - a repeated problem
   - a continuing problem
   - an improvement over time

4. Use the recorded status values (OK, WARNING, CRITICAL)
   together with the usage percentages.

5. Do not assume that a high value automatically means
   there is a specific underlying cause.

6. If you suggest a possible cause, clearly identify it
   as a possibility rather than a confirmed fact.

7. Do not invent information that is not present in
   the health report.

8. If the report does not contain enough information
   to answer the question, clearly explain what
   information is missing.

9. Explain technical concepts in a beginner-friendly way.

10. When discussing historical data, mention the relevant
    dates and values when they help support your answer.
11. Do not describe an increase in resource usage as an
    improvement unless the data actually shows a reduction.

12. Do not make medical-style or absolute statements such as
    "nothing to worry about" or "no cause for alarm."
    Instead, describe what the recorded monitoring status
    indicates.

13. When interpreting a metric, distinguish between:
    - what the data directly shows
    - what can reasonably be inferred
    - possible explanations that are not confirmed.

14. Do not treat a small number of historical samples as
    proof of long-term system behavior.
"""

    # --------------------------------------------------------
    # 7. Send the question and health data to Gemini
    # --------------------------------------------------------

    interaction = client.interactions.create(
        model=model,
        input=prompt
    )

    # --------------------------------------------------------
    # 8. Display Gemini's answer
    # --------------------------------------------------------

    print("\nAI:", interaction.output_text)
    print()