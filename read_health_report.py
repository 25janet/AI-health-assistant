import json

with open("json/health_report.json","r",encoding="utf-8") as file:
    health_report = json.load(file)

print(health_report)