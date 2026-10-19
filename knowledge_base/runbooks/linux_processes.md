# Linux Process Troubleshooting Runbook

## 1. Purpose

This runbook explains how to inspect running processes, identify resource-intensive applications, investigate abnormal behavior, and verify that corrective actions worked.

## 2. Common Symptoms

- High CPU usage.
- Excessive memory consumption.
- An unresponsive or hung application.
- A process consuming resources unexpectedly.
- A service that has stopped or repeatedly restarts.

## 3. Inspect Running Processes

Display running processes:

```bash
ps aux
```

Display processes in real time:

```bash
top
```

Display processes in a tree:

```bash
pstree -p
```

If `pstree` is unavailable, use:

```bash
ps -ef --forest
```

## 4. Identify Resource-Intensive Processes

Find processes consuming the most CPU:

```bash
ps aux --sort=-%cpu | head -n 10
```

Find processes consuming the most memory:

```bash
ps aux --sort=-%mem | head -n 10
```

Check overall system load:

```bash
uptime
```

Check available memory:

```bash
free -h
```

Investigate whether the process is expected to consume these resources before taking action.

## 5. Inspect a Specific Process

Find a process by name:

```bash
pgrep -a PROCESS_NAME
```

Inspect its status and resource usage:

```bash
ps -p PID -o pid,ppid,stat,%cpu,%mem,etime,cmd
```

Replace `PROCESS_NAME` with the actual process name and `PID` with its process ID.

For a systemd-managed service, inspect its status:

```bash
systemctl status SERVICE_NAME
```

View recent service logs:

```bash
journalctl -u SERVICE_NAME --since "1 hour ago"
```

## 6. Investigate and Correct the Problem

1. Identify the process responsible for the abnormal resource usage.
2. Check its purpose, parent process, and associated service.
3. Review application and system logs for errors.
4. Determine whether the behavior is expected, temporary, or abnormal.
5. Use the application's documented recovery procedure.
6. Restart a service only when appropriate and authorized.

If a process must be terminated, first try a graceful signal:

```bash
kill PID
```

Check whether it has stopped:

```bash
ps -p PID
```

Use `kill -9 PID` only as a last resort when a normal termination fails and termination is justified. It prevents the process from handling the termination signal and cleaning up normally.

Do not terminate critical system processes simply because they use CPU or memory.

## 7. Verification

After corrective action:

- Confirm that the process is in the expected state.
- Recheck CPU and memory usage using `top` or `ps`.
- Confirm that the relevant service is healthy.
- Inspect logs for recurring errors.
- Verify that the original application operation works.

## 8. Quick Reference

| Task | Command |
|---|---|
| List processes | `ps aux` |
| Monitor processes | `top` |
| Highest CPU usage | `ps aux --sort=-%cpu \| head -n 10` |
| Highest memory usage | `ps aux --sort=-%mem \| head -n 10` |
| Find a process | `pgrep -a PROCESS_NAME` |
| Inspect service | `systemctl status SERVICE_NAME` |
| Inspect service logs | `journalctl -u SERVICE_NAME --since "1 hour ago"` |

## 9. Summary

Identify the process, investigate its behavior, apply a safe corrective action, and verify that both resource usage and application behavior have improved.
