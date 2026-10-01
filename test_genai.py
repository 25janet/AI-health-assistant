# ============================================================
# AI Linux Health Assistant - OpenAI API Connection Test
# ============================================================
# Purpose:
# This file tests whether our Python application can connect
# to the OpenAI API and receive a response from an LLM.
#
# This is only a test. Later, we will replace the simple
# test question with our actual Linux health report.
# ============================================================


# ------------------------------------------------------------
# 1. Import the required libraries
# ------------------------------------------------------------

# 'os' allows Python to interact with environment variables.
# We will use it to retrieve the model name from our .env file.
import os

# 'load_dotenv' loads the variables stored in our .env file
# into the environment so that Python can access them.
from dotenv import load_dotenv

# 'OpenAI' is the Python client provided by the OpenAI SDK.
# It allows our Python program to communicate with the OpenAI API.
from google import genai


# ------------------------------------------------------------
# 2. Load environment variables from the .env file
# ------------------------------------------------------------

# Read the .env file in the project directory.
#
# Our .env file contains configuration such as:
#
# OPENAI_API_KEY=our_secret_key
# OPENAI_MODEL=the_model_we_want_to_use
#
# We keep these values outside our Python code so that
# sensitive information is not hard-coded into the program.
load_dotenv()


# ------------------------------------------------------------
# 3. Get the model name from the environment
# ------------------------------------------------------------

# os.getenv() retrieves the value of an environment variable.
#
# For example, if .env contains:
#
# OPENAI_MODEL=gpt-5.5
#
# then:
#
# model = os.getenv("OPENAI_MODEL")
#
# gives us:
#
# model = "gpt-5.5"
#
# This allows us to change the model from the .env file
# without modifying this Python program.
model = os.getenv("GEMINI_MODEL")


# ------------------------------------------------------------
# 4. Create the OpenAI client
# ------------------------------------------------------------

# Create an OpenAI client that our Python program will use
# to communicate with the OpenAI API.
#
# The OpenAI SDK automatically looks for the
# OPENAI_API_KEY environment variable for authentication.
#
# We do NOT put the actual API key directly in this file.
client = genai()


# ------------------------------------------------------------
# 5. Send a request to the LLM
# ------------------------------------------------------------

# client.responses.create() sends a request to the
# OpenAI Responses API.
#
# 'model' tells the API which model should process our request.
#
# 'input' contains the instruction/question we want
# the LLM to respond to.
#
# For now, we are using a simple test question.
# Later, this input will contain information from:
#
# json/health_report.json
#
# so that the LLM can analyze our Linux system health.
response = client.responses.create(
    model=model,
    input=(
        "Say hello and explain in one sentence "
        "what a Linux health monitoring system does."
    )
)


# ------------------------------------------------------------
# 6. Display the LLM's response
# ------------------------------------------------------------

# response.output_text extracts the actual text generated
# by the LLM from the API response.
#
# print() then displays that text in our terminal.
print(response.output_text)