# Linux System Health Summary Runbook

## 1. Purpose

This runbook explains how to review a Linux health report, interpret CPU, memory, disk, and network results, identify warnings, and verify the overall system condition.

## 2. Review the Health Check Output

From the project root, inspect the raw health log:

```bash
cat data/raw/health.log
```

Inspect the processed health report:

```bash
cat data/processed/health_report.json
```

Display the JSON in a readable format, if `jq` is installed:

```bash
jq . data/processed/health_report.json
```

Check that the files exist and contain recent results before interpreting them.

## 3. Check System Resources

### CPU

```bash
uptime
top
```

Investigate sustained high CPU usage, unusual load, or resource-intensive processes.

### Memory

```bash
free -h
ps aux --sort=-%mem | head -n 10
```

Investigate low available memory, excessive swapping, and processes consuming unusually large amounts of memory.

### Disk

```bash
df -h
df -i
```

Investigate filesystems with little free space or exhausted inodes.

### Network

```bash
ip -br addr
ip route show
ping -c 4 8.8.8.8
```

Check interface state and routing. Interpret ping results carefully because ICMP traffic may be blocked even when other connectivity works.

## 4. Interpret Health Status

The project health checker uses these resource thresholds:

| Utilization | Status |
|---|---|
| Below 70% | OK |
| 70% through 85% | WARNING |
| Above 85% | CRITICAL |

Apply these thresholds only to the metrics for which the health checker is configured to use them. Network reachability and other checks require their own interpretation.

- **OK:** No configured threshold has been breached.
- **WARNING:** Investigate the metric and look for developing resource pressure.
- **CRITICAL:** Prioritize investigation and take appropriate corrective action.

A low utilization percentage does not automatically mean that a system is healthy. A failed service, broken route, or application error can occur even when resource usage is low.

## 5. Investigate Warnings and Critical Results

1. Identify the affected resource or failed check.
2. Confirm that the report reflects the latest health-check run.
3. Run the relevant diagnostic commands.
4. Identify the likely cause using process information and system logs.
5. Apply a safe corrective action.
6. Rerun the health check and compare the results.

Review system logs when necessary:

```bash
journalctl --since "1 hour ago"
```

Kernel-related events can be inspected with:

```bash
journalctl -k --since "1 hour ago"
```

## 6. Verify the Final Health Summary

After remediation:

- Confirm that the health-check script completed successfully.
- Confirm that the raw log contains the latest results.
- Confirm that the JSON report is valid and reflects the latest run.
- Recheck the affected CPU, memory, disk, or network metric.
- Confirm that the original failure is resolved.
- Check whether warnings or critical conditions persist.

Validate the report's JSON syntax with Python:

```bash
python3 -m json.tool data/processed/health_report.json
```

A successful JSON validation confirms syntax, not the accuracy or freshness of the report.

## 7. Operational Notes

- Do not delete files or stop processes without understanding their purpose.
- Do not assume that a successful health-check script means every subsystem is healthy.
- Compare current readings with previous results when available.
- Record unresolved issues, their impact, and the next troubleshooting action.
- Treat a missing, stale, or invalid report as a monitoring problem that requires investigation.

## 8. Summary

Review the latest health report, identify abnormal metrics, investigate the underlying cause, apply a safe correction, and rerun the health check to verify recovery.
