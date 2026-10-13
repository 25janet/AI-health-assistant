# Linux CPU Usage Troubleshooting Runbook

## 1. Purpose

This runbook provides a systematic procedure for investigating high CPU usage on Linux systems. It helps an administrator identify CPU-intensive processes, examine system load, distinguish CPU saturation from other resource bottlenecks, and verify whether corrective actions have improved system performance.

The goal is to collect evidence before making changes. High CPU usage is not automatically a fault because some applications are expected to perform intensive computations.

## 2. Symptoms of High CPU Usage

Possible symptoms include:

* Applications responding slowly.
* Commands taking longer than expected to finish.
* High CPU utilization reported by monitoring tools.
* High system load averages.
* Increased response times for services.
* Fans running frequently at high speed on physical machines.
* Background jobs or processes consuming substantial CPU resources.

These symptoms can also result from memory pressure, disk I/O, network delays, or application-level problems. Investigate multiple indicators before deciding that CPU saturation is the cause.

## 3. Step One: Inspect CPU and System Load

Run:

```bash
uptime
```

This displays how long the system has been running, the number of logged-in users, and the load averages for the last 1, 5, and 15 minutes.

Example:

```text
load average: 2.10, 1.80, 1.50
```

Load average represents the average number of tasks that are runnable or waiting in uninterruptible sleep, commonly while waiting for I/O. It is not a direct percentage of CPU utilization.

Interpret load averages in relation to the number of available CPU cores. For example, a sustained load average of 8 on a system with 2 CPU cores warrants investigation, but the load alone does not prove CPU saturation.

To determine the number of CPU processing units available to the current environment, run:

```bash
nproc
```

On Linux systems, `nproc` reports the processing units available to the current process. Container limits, CPU affinity, and virtualization can affect the result.

## 4. Step Two: Monitor CPU Utilization

Run:

```bash
top
```

The `top` command displays running processes and periodically refreshes system statistics.

Inspect the CPU summary and process list.

Useful CPU fields include:

* `%us`: CPU time spent running user-space processes.
* `%sy`: CPU time spent executing kernel code.
* `%id`: percentage of CPU time spent idle.
* `%wa`: CPU time spent waiting for I/O to complete.
* `%st`: CPU time stolen by the hypervisor in virtualized environments, where reported.

Useful process fields include:

* `PID`: process identifier.
* `USER`: account running the process.
* `%CPU`: CPU utilization attributed to the process.
* `%MEM`: percentage of physical memory used.
* `COMMAND`: process or command name.

In interactive `top`, press `P` to sort processes by CPU usage and `q` to quit.

A high `%wa` value may indicate an I/O bottleneck rather than a CPU computation bottleneck. A high `%st` value in a virtual machine may indicate contention for physical CPU resources on the host.

## 5. Step Three: Identify CPU-Heavy Processes

Run:

```bash
ps aux --sort=-%cpu | head -n 10
```

This lists processes ordered by CPU percentage and displays up to ten entries, including the header.

Pay attention to:

* Processes consistently consuming substantial CPU.
* Unexpected commands or unfamiliar executables.
* Repeatedly restarting processes.
* Multiple instances of the same process consuming resources.
* CPU-intensive jobs that are not expected to be running.

A single snapshot shows only a moment in time. Repeat the command or use `top` to determine whether CPU consumption is sustained.

Do not terminate a process solely because it has a high CPU percentage. First establish what it does, whether it belongs to a critical service, and whether its workload is expected.

## 6. Step Four: Collect CPU Statistics Over Time

If the `sysstat` package is installed, run:

```bash
mpstat 1 5
```

This reports CPU statistics at one-second intervals for five samples.

If `mpstat` is unavailable, the command may require installation of the `sysstat` package using the distribution's package manager and appropriate administrative permissions.

Compare the samples instead of relying on one measurement. Sustained low idle time together with high CPU demand provides stronger evidence of CPU saturation than a brief spike.

You can also inspect per-CPU statistics with:

```bash
top
```

This helps reveal whether work is concentrated on one CPU or spread across several processing units.

## 7. Step Five: Check CPU-Related Process Behavior

For a closer look at a particular process, identify its PID and run:

```bash
ps -p PID -o pid,ppid,stat,%cpu,%mem,etime,cmd
```

Replace `PID` with the actual numeric process identifier.

The output includes:

* `PID`: the process identifier.
* `PPID`: the parent process identifier.
* `STAT`: process state.
* `%CPU`: reported CPU utilization.
* `%MEM`: reported memory utilization.
* `ETIME`: elapsed time since the process started.
* `CMD`: command associated with the process.

Check whether the process is expected to be running and whether its CPU use corresponds to its workload.

If the process belongs to a systemd service, inspect the service status using:

```bash
systemctl status SERVICE_NAME
```

Replace `SERVICE_NAME` with the actual service name. Use appropriate permissions if required.

A failed or repeatedly restarting service may have a different underlying cause from a normally running CPU-intensive application.

## 8. Step Six: Examine Recent System Logs

To inspect recent system messages, run:

```bash
journalctl --since "1 hour ago"
```

To narrow the output to a particular service, run:

```bash
journalctl -u SERVICE_NAME --since "1 hour ago"
```

Replace `SERVICE_NAME` with the relevant systemd service name.

Look for:

* Repeated service restarts.
* Application errors occurring alongside CPU spikes.
* Scheduled jobs starting unexpectedly.
* Resource-related warnings.
* Repeated failures that could cause retry loops.

Kernel and system logs may require elevated privileges. Use `sudo` only when permitted and necessary.

Logs may not identify the cause of every CPU spike. Correlate timestamps with process measurements and application behavior.

## 9. Step Seven: Investigate Related Resource Bottlenecks

High load does not always mean the CPUs are fully utilized. Check other resources when the evidence suggests a different bottleneck.

### Memory pressure

Run:

```bash
free -h
```

Review the available memory and consider whether swapping or memory exhaustion could be affecting performance.

### Disk and I/O pressure

Run:

```bash
vmstat 1 5
```

Inspect the `wa` CPU field and other reported activity. If disk I/O is suspected, additional tools such as `iostat` may help when available.

### Network or application delays

If CPU utilization is low but an application remains slow, investigate network latency, dependency failures, locks, or other application-specific causes rather than assuming the CPU is the problem.

## 10. Step Eight: Apply Safe Corrective Actions

Choose a corrective action based on the evidence and your operational permissions.

Possible actions include:

* Allowing a legitimate CPU-intensive task to finish.
* Rescheduling a non-urgent batch job.
* Investigating an application retry loop or runaway workload.
* Restarting an affected service only when justified and approved.
* Optimizing application configuration or code through the normal change process.
* Adjusting workload concurrency or resource limits when supported by the environment and approved by the system owner.

Avoid immediately killing processes, disabling services, or changing system-wide settings without understanding the consequences.

## 11. Verification

After an approved corrective action, run:

```bash
uptime
```

Then inspect CPU utilization:

```bash
top
```

You can also repeat:

```bash
ps aux --sort=-%cpu | head -n 10
```

Compare the new results with the earlier measurements.

Look for sustained improvements in CPU utilization, load, process behavior, and application responsiveness. A single lower reading does not necessarily prove that the issue has been resolved.

## 12. Troubleshooting Summary

| Symptom                           | Initial command                     | What to investigate                            |
| --------------------------------- | ----------------------------------- | ---------------------------------------------- |
| High system load                  | `uptime`                            | Load averages relative to available CPU units  |
| High CPU utilization              | `top`                               | CPU summary and continuously active processes  |
| CPU-heavy processes               | `ps aux --sort=-%cpu \| head -n 10` | Process identity and sustained CPU consumption |
| Per-CPU utilization               | `mpstat 1 5`                        | Utilization trends across CPU samples          |
| Suspected service problem         | `systemctl status SERVICE_NAME`     | Service state and restart behavior             |
| Recent errors                     | `journalctl --since "1 hour ago"`   | Errors and events matching the incident time   |
| Possible memory or I/O bottleneck | `free -h` and `vmstat 1 5`          | Available memory, swapping, and I/O wait       |

## 13. Important Notes

* High CPU utilization can be normal during compilation, data processing, compression, or other computationally intensive workloads.
* Load average includes tasks waiting in uninterruptible sleep, so it must not be interpreted as a direct CPU percentage.
* Container CPU limits and virtual-machine scheduling can affect observed performance.
* Commands and available fields can differ between Linux distributions and environments.
* Gather measurements before and after corrective actions to support evidence-based troubleshooting.
