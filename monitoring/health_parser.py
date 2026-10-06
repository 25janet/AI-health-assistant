import json

json_output = []

current_date = None
in_summary = False
in_top_cpu = False
in_top_memory = False

metrics = {}
top_cpu = []
top_memory = []

with open("data/raw/health.log", "r", encoding="utf-8") as file:

    for line in file:

        stripped_line = line.strip()

        # --------------------------------------------------
        # 1. Capture the date
        # --------------------------------------------------
        if stripped_line.startswith("Date:"):
            current_date = stripped_line.replace("Date:", "").strip()

        # --------------------------------------------------
        # 2. Detect Top CPU Processes section
        # --------------------------------------------------
        elif "Top CPU Processes:" in line:

            in_top_cpu = True
            in_top_memory = False
            top_cpu = []

        # --------------------------------------------------
        # 3. Detect Top Memory Processes section
        # --------------------------------------------------
        elif "Top Memory Processes:" in line:

            in_top_cpu = False
            in_top_memory = True
            top_memory = []

        # --------------------------------------------------
        # 4. Detect Health Check Summary
        # --------------------------------------------------
        elif "Health check Summary" in line:

            in_top_cpu = False
            in_top_memory = False

            in_summary = True
            metrics = {}

        # --------------------------------------------------
        # 5. Process Top CPU / Top Memory entries
        # --------------------------------------------------
        elif in_top_cpu or in_top_memory:

            # Skip empty lines
            if not stripped_line:
                continue

            # Example:
            # 2884 jenkins 3.4 16.8 java

            parts = stripped_line.split()

            # We expect:
            # PID USER CPU% MEM% COMMAND
            if len(parts) >= 5:

                pid = int(parts[0])
                user = parts[1]
                cpu_percent = float(parts[2])
                memory_percent = float(parts[3])
                command = parts[4]

                process = {
                    "pid": pid,
                    "user": user,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "command": command
                }

                if in_top_cpu:
                    top_cpu.append(process)

                elif in_top_memory:
                    top_memory.append(process)

        # --------------------------------------------------
        # 6. Process lines inside Health Check Summary
        # --------------------------------------------------
        elif in_summary:

            # Detect the end of the summary
            if stripped_line.startswith("========="):

                in_summary = False

                log_entry = {
                    "date": current_date,

                    "status": metrics,

                    "processes": {
                        "top_cpu": top_cpu,
                        "top_memory": top_memory
                    }
                }

                json_output.append(log_entry)

            # Process metric lines
            elif ":" in stripped_line:

                key, val = stripped_line.split(":", 1)

                # Example:
                # val = "37 [OK]"
                # parts = ["37", "[OK]"]
                parts = val.strip().split()

                number = int(parts[0])

                status = parts[1].strip("[]")

                metrics[key.strip().lower()] = {
                    "usage_percent": number,
                    "status": status
                }


# --------------------------------------------------
# 7. Convert Python data to JSON
# --------------------------------------------------

json_string = json.dumps(json_output, indent=4)


# --------------------------------------------------
# 8. Save JSON file
# --------------------------------------------------

with open(
    "data/processed/health_report.json",
    "w",
    encoding="utf-8"
) as json_file:

    json_file.write(json_string)


print("Health report successfully converted to JSON.")