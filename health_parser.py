import json

json_output = []

current_date = None
in_summary = False
metrics = {}

with open("log/health.log", "r", encoding="utf-8") as file:
    for line in file:
        stripped_line = line.strip()

        # 1. Capture the date
        if stripped_line.startswith("Date:"):
            current_date = stripped_line.replace("Date:", "").strip()

        # 2. Detect the Health Check Summary
        elif "Health check Summary" in line:
            in_summary = True
            metrics = {}

        # 3. Process lines inside the summary
        elif in_summary:

            # Detect the end of the summary
            if stripped_line.startswith("========="):
                in_summary = False

                log_entry = {
                    "date": current_date,
                    "status": metrics
                }

                json_output.append(log_entry)

            # Process metric lines
            elif ":" in stripped_line:
                key, val = stripped_line.split(":", 1)

                # Example:
                # val = "28 [OK]"
                # parts = ["28", "[OK]"]
                parts = val.strip().split()

                # Take only the number
                number = int(parts[0])

                metrics[key.strip().lower()] = number


# Convert Python data to JSON
json_string = json.dumps(json_output, indent=4)

# Save JSON file
with open("json/health_report.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_string)

print("Health report successfully converted to JSON.")