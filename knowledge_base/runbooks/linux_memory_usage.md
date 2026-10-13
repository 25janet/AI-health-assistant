
# Linux Memory Usage Troubleshooting Runbook

## 1. Purpose

This runbook explains how to investigate high memory usage on a Linux system. It provides diagnostic commands for examining available memory, swap usage, and processes that consume memory.

The goal is to identify where memory is being used before deciding whether corrective action is necessary.

## 2. Symptoms

Possible indicators of memory pressure include:

- Available memory becoming very low.
- Swap usage increasing.
- Applications becoming slow or unresponsive.
- Processes being terminated by the Linux out-of-memory mechanism.
- Services failing when they cannot allocate enough memory.

High memory usage alone does not prove that a system has a memory problem. Linux uses some available memory for caches, which can be reclaimed when needed.

## 3. Step One: Inspect Overall Memory Usage

Run:

```bash
free -h
```

This command displays total, used, free, shared, cache/buffer, and available memory.

Pay particular attention to the `available` value. It estimates how much memory can be used by applications without requiring significant swapping.

Do not interpret the `free` column alone as the amount of memory available to applications.

## 4. Step Two: Monitor Memory Continuously

Run:

```bash
vmstat 1 5
```

This displays five samples of system activity at one-second intervals.

Useful fields include:

- `free`: memory currently unused.
- `si`: memory swapped in per interval.
- `so`: memory swapped out per interval.
- `r`: processes waiting to run.
- `b`: processes blocked waiting for resources.

Repeated nonzero swap activity can indicate memory pressure, but it should be interpreted alongside available memory and overall system behavior.

## 5. Step Three: Identify Memory-Heavy Processes

Run:

```bash
ps aux --sort=-%mem | head -n 10
```

This lists processes ordered by memory percentage, showing up to ten entries.

Useful columns include:

- `USER`: account running the process.
- `PID`: process identifier.
- `%MEM`: percentage of physical memory used.
- `%CPU`: CPU utilization.
- `COMMAND`: process or command name.

A process using substantial memory is not automatically faulty. Investigate its expected workload, normal behavior, and memory usage over time before taking action.

## 6. Step Four: Inspect Swap Usage

Run:

```bash
swapon --show
```

This displays configured swap devices or files and their usage.

Swap provides additional virtual memory by using disk storage. It is slower than RAM, so sustained heavy swapping may affect performance.

The presence of swap usage alone does not prove that the system is currently under severe memory pressure.

## 7. Step Five: Check for Out-of-Memory Events

On systems using systemd's journal, run:

```bash
journalctl -k --since "1 hour ago"
```

Review the output for messages containing terms such as:

- `Out of memory`
- `oom-kill`
- `Killed process`

These messages can help determine whether the Linux kernel reported memory exhaustion or terminated a process.

Access to kernel logs may require elevated privileges. If permitted and necessary, use:

```bash
sudo journalctl -k --since "1 hour ago"
```

An absent message does not guarantee that no memory problem occurred; the relevant event may be outside the selected time range or unavailable in the logs.

## 8. Step Six: Compare Memory Usage Over Time

Repeat `free -h` and process inspection at suitable intervals when investigating a suspected recurring problem.

Compare:

- Available memory.
- Swap activity and usage.
- The processes consuming the most memory.
- Application responsiveness.
- Relevant kernel or service log messages.

A single snapshot may not be enough to establish a persistent memory leak or recurring problem.

## 9. Remediation Principles

1. Confirm whether available memory is genuinely low.
2. Identify the processes consuming the most memory.
3. Check whether the usage is expected for the workload.
4. Review relevant application and system logs.
5. Investigate repeated memory growth before concluding that a leak exists.
6. Avoid terminating processes without understanding their purpose and impact.
7. Back up important data and follow approved operational procedures before making significant changes.
8. Recheck memory usage after any approved remediation.

Do not automatically kill processes merely because their memory usage is high.

## 10. Verification

After an approved corrective action, run:

```bash
free -h
```

If necessary, inspect the process list again:

```bash
ps aux --sort=-%mem | head -n 10
```

Compare the results with the earlier observations to determine whether memory availability or process usage changed.

## 11. Safety Notes

- Diagnostic commands should be preferred before corrective actions.
- Do not terminate critical system services based solely on their memory percentage.
- Do not assume that cache usage represents wasted memory.
- Do not claim a memory leak without supporting evidence.
- Destructive or disruptive actions require appropriate human review.