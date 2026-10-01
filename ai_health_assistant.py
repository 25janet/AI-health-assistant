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

with open("json/health_report.json", "r", encoding="utf-8") as file:
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
of their Linux system.

Below is the Linux health monitoring data:

{health_report_text}

The user has asked:

{user_question}

Answer the user's question using the health data provided.

Important:
- Do not invent information that is not present in the report.
- If the report does not contain enough information to answer,
  clearly say what additional information would be needed.
- Explain technical concepts in a beginner-friendly way.
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