# Linux Disk Usage Troubleshooting Runbook

## 1. Purpose

This runbook describes how to investigate high disk usage on a Linux system. It provides diagnostic commands, explains what their output means, and identifies safe next steps.

## 2. Symptoms

Possible indicators of a disk-space problem include:

* Disk usage reaching the configured warning or critical threshold.
* Applications failing to write files.
* Log files growing unexpectedly.
* Services reporting that no space is available.
* Systems experiencing problems creating temporary files.

A high disk-usage percentage indicates limited remaining capacity, but it does not by itself identify the cause.

## 3. Step One: Check Filesystem Usage

Run:

```bash
df -h
```

The command displays filesystem capacity in human-readable units.

Important columns include:

* `Size`: total filesystem capacity.
* `Used`: space currently used.
* `Avail`: space available to ordinary users.
* `Use%`: percentage of space used.
* `Mounted on`: directory where the filesystem is accessible.

Focus on the filesystem whose usage is high. Different filesystems can have different capacity limits.

## 4. Step Two: Check Inode Usage

Run:

```bash
df -i
```

Inodes track filesystem objects such as files and directories. A filesystem can run out of available inodes even when it still has free storage capacity.

Compare inode usage with the filesystem's disk-space usage.

## 5. Step Three: Identify Large Directories

To inspect the largest directories immediately below the root directory, run:

```bash
sudo du -xhd1 / 2>/dev/null
```

To investigate a particular directory, substitute its path. For example:

```bash
sudo du -xhd1 /var 2>/dev/null
```

The `-x` option keeps the search on the same filesystem. The `-h` option displays readable sizes, and `-d1` limits the displayed directory depth.

These commands inspect directory sizes; they do not delete files.

## 6. Step Four: Inspect System Logs

Check how much disk space systemd's journal uses:

```bash
journalctl --disk-usage
```

If logs consume substantial space, investigate their growth and the applicable log-retention policy before performing cleanup.

## 7. Step Five: Inspect Docker Storage

On systems that use Docker, run:

```bash
docker system df
```

This reports Docker's disk usage, including images, containers, volumes and build cache.

Identify which resources consume space before removing anything. Containers and volumes may hold important application data.

## 8. Remediation Principles

1. Identify the affected filesystem before taking action.
2. Determine which files or directories account for the usage.
3. Check whether the files are needed by applications or services.
4. Review logs and retention policies when log growth is suspected.
5. Back up important data before removing or modifying it.
6. Use approved cleanup procedures and avoid deleting files blindly.
7. Recheck disk and inode usage after remediation.

Do not automatically delete files merely because disk usage is high.

## 9. Verification

After an approved remediation, run:

```bash
df -h
df -i
```

Compare the new values with the original measurements to determine whether available capacity or inode availability improved.

## 10. Safety Note

These diagnostic commands are intended for investigation. Cleanup operations should be selected according to the actual cause, the system's requirements and the applicable operational procedures. Destructive actions require human review and approval.
