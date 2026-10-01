import json
json_output = []


current_date = None
in_summary = False
metrics = {}


with open("log/health.log", "r", encoding="utf-8") as file:
    for line in file:
        stripped_line = line.strip()
        
        # 1. Capture the date string
        if stripped_line.startswith("Date:"):
            # Splits "Date: Sat Aug 22..." into just "Sat Aug 22..."
            current_date = stripped_line.replace("Date:", "").strip()
        
        # 2. Detect the start of the Health check Summary block
        elif "Health check Summary" in line:
            in_summary = True
            metrics = {} # Reset metrics dictionary for this block
            
        # 3. Process lines inside the summary block
        elif in_summary:
            # Look for metric lines like "Memory:  11 [OK]"
            if ":" in stripped_line and not stripped_line.startswith("=="):
                key, val = stripped_line.split(":", 1)
                metrics[key.strip().lower()] = val.strip()
             # Detect the end of the block
            elif stripped_line.startswith("========="):
                in_summary = False
                
                # Assemble the structured object
                log_entry = {
                    "date": current_date,
                    "status": metrics
                }
                json_output.append(log_entry)

# Convert the Python list/dictionaries into a pretty-printed JSON string
json_string = json.dumps(json_output, indent=4)
with open("json/health_report.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_string)

