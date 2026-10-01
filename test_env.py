import os
#Load and read from the .env file using python one requires to load dotenv 
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")
log_file = os.getenv("LOG_FILE")
report_file = os.getenv("REPORT_FILE")

print("Api key configured: ", api_key is not None)
print("Model: ",model)
print("Log file: ",log_file)
print("Report file: ",report_file)