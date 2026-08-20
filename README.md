# 🤖 AI Linux Health Assistant

An evolving DevOps project that starts as a **Bash-based Linux system health checker** and gradually develops into an **AI-powered health assistant** using **LLMs, RAG, automation, and DevOps tools**.

The goal is to build the project incrementally while learning Linux, Bash, Git, GitLab, CI/CD, monitoring, and eventually AI integration.

---

## 🎯 Project Goal

The final goal is to create an assistant that can:

* Monitor Linux system health
* Collect CPU, memory, disk, process, and network information
* Automatically run health checks using cron
* Store health-check results in logs
* Detect potential problems
* Analyze system logs
* Use an LLM to explain problems in simple language
* Use RAG to retrieve relevant troubleshooting documentation
* Suggest possible solutions
* Eventually integrate with DevOps workflows

The project will be built **step by step**, rather than attempting everything at once.

---

# 🏗️ Project Evolution

The project will grow through several stages.

```text
Stage 1
Linux + Bash
     ↓
Stage 2
Cron + Logging
     ↓
Stage 3
Git + GitLab
     ↓
Stage 4
Monitoring + Alerts
     ↓
Stage 5
LLM Integration
     ↓
Stage 6
RAG
     ↓
Stage 7
AI DevOps Assistant
```

---

# 🟢 Stage 1 — Linux Health Checker

The first version is a Bash script that collects basic Linux system information.

### Current checks

* Hostname
* Current user
* Date and time
* Memory usage
* Disk usage
* Network information
* IP addresses
* Routing information
* Listening ports

Example:

```text
========== SYSTEM HEALTH CHECK ==========

Hostname: my-linux-machine
User: user

----- MEMORY USAGE -----
Memory usage: 42%
Memory status: OK

----- DISK USAGE -----
Disk usage: 38%
Disk status: OK

----- NETWORK -----
Hostname: my-linux-machine
IP Address: 192.168.1.10

Default route:
default via 192.168.1.1

Listening ports:
...

========= CHECK COMPLETE =========
```

### Technologies

* Linux
* Bash
* `df`
* `free`
* `ip`
* `ss`
* `awk`
* `grep`

---

# 🟡 Stage 2 — Automation with Cron

The health checker will eventually run automatically using cron.

Example:

```bash
*/15 * * * * /path/to/health-check.sh >> /path/to/health.log 2>&1
```

This allows the system to perform health checks every 15 minutes without manual execution.

The results will be stored in log files.

```text
Health Check
     ↓
Cron
     ↓
Bash Script
     ↓
health.log
```

---

# 🟠 Stage 3 — Git and GitLab

The project will be managed using Git and GitLab.

### Git workflow

```text
Create feature
     ↓
Create branch
     ↓
Develop
     ↓
Test
     ↓
Commit
     ↓
Push to GitLab
     ↓
Merge
```

Example branches:

```text
main
├── feature/memory-check
├── feature/disk-check
├── feature/network-check
├── feature/logging
└── feature/ai-analysis
```

The project will use GitLab to practice:

* Repositories
* Branches
* Commits
* Merge requests
* Remote repositories
* CI/CD

---

# 🔵 Stage 4 — Monitoring and Alerts

The project can eventually become more than a simple health checker.

Instead of only reporting:

```text
Memory usage: 91%
```

the system could identify this as a problem:

```text
WARNING

Memory usage: 91%

Status: CRITICAL
```

Possible future features:

* Threshold-based alerts
* Log analysis
* Process monitoring
* Service monitoring
* CPU monitoring
* Disk monitoring
* Network connectivity checks

---

# 🟣 Stage 5 — LLM Integration

Once the traditional health checker works, an LLM can be introduced.

The health-check results could be sent to an AI system for analysis.

Example input:

```text
Memory usage: 91%
Disk usage: 87%
CPU usage: 94%
Network: OK
```

The LLM could generate an explanation such as:

```text
The system is experiencing high resource usage.

Memory and CPU usage are both above the configured
thresholds. Further investigation should focus on
processes consuming the most resources.
```

The LLM would help with:

* Explaining errors
* Summarizing logs
* Identifying possible causes
* Suggesting troubleshooting steps
* Turning technical output into human-readable explanations

---

# 🧠 Stage 6 — RAG Integration

The next major feature will be **Retrieval-Augmented Generation (RAG)**.

The assistant will have access to a knowledge base containing information such as:

```text
knowledge-base/
├── linux.md
├── networking.md
├── docker.md
├── kubernetes.md
├── troubleshooting.md
├── runbooks/
└── incident-reports/
```

Instead of asking the LLM to answer only from its general knowledge, the system will first retrieve relevant information.

```text
User Question
      ↓
Retrieve relevant documents
      ↓
Relevant context
      ↓
LLM
      ↓
Answer
```

For example:

> Why is memory usage above 90%?

The RAG system could retrieve a company troubleshooting procedure:

```text
If memory usage exceeds 85%:

1. Check memory-consuming processes.
2. Review application logs.
3. Check recent deployments.
4. Investigate possible memory leaks.
```

The LLM can then use this information when generating its response.

---

# 🚀 Stage 7 — AI DevOps Health Assistant

The final version could combine everything:

```text
                    Linux System
                         │
                         ↓
                  Health Checker
                         │
                         ↓
                       Cron
                         │
                         ↓
                       Logs
                         │
              ┌──────────┴──────────┐
              ↓                     ↓
          Monitoring              RAG
              │                     │
              └──────────┬──────────┘
                         ↓
                        LLM
                         ↓
                 AI Health Assistant
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          Explain     Diagnose    Recommend
```

The assistant could answer questions such as:

> What is wrong with my system?

> Why did memory usage suddenly increase?

> Which process is consuming the most resources?

> Is the disk usage dangerous?

> What should I investigate first?

> Has this problem happened before?

---

# 🛡️ Human Approval

The AI should not automatically make dangerous production changes.

A safer design is:

```text
AI detects problem
      ↓
AI investigates
      ↓
AI recommends action
      ↓
Human reviews
      ↓
Human approves
      ↓
Automation executes
```

This keeps the engineer in control.

---

# 🧰 Planned Technology Stack

## DevOps

* Linux
* Bash
* Git
* GitLab
* GitLab CI/CD
* Docker
* Kubernetes
* Cloud platform

## Monitoring

Potential future technologies:

* Prometheus
* Grafana
* Log aggregation tools

## AI

* Python
* LLM APIs
* Prompt engineering
* Embeddings
* Vector databases
* RAG
* AI agents/tool calling

---

# 📁 Possible Final Project Structure

```text
ai-linux-health-assistant/
│
├── health-check.sh
│
├── scripts/
│   ├── memory.sh
│   ├── disk.sh
│   ├── network.sh
│   └── processes.sh
│
├── logs/
│   └── health.log
│
├── knowledge-base/
│   ├── linux.md
│   ├── networking.md
│   ├── docker.md
│   └── troubleshooting.md
│
├── ai/
│   ├── assistant.py
│   ├── rag.py
│   └── llm.py
│
├── tests/
│
├── .gitignore
├── README.md
└── requirements.txt
```

This structure is only a future target. The project will start much smaller.

---

# 📚 Learning Roadmap

The project will be developed alongside learning.

### Phase 1 — Linux

* Files and directories
* Permissions
* Processes
* Networking
* Disk management
* Logging

### Phase 2 — Bash

* Variables
* Conditions
* Loops
* Functions
* Input
* Exit codes
* Command substitution
* Redirection

### Phase 3 — Automation

* Cron
* Logging
* Scheduled tasks

### Phase 4 — Git/GitLab

* Branching
* Commits
* Merge requests
* GitLab CI/CD

### Phase 5 — DevOps

* Docker
* Kubernetes
* Cloud
* Monitoring

### Phase 6 — AI

* Python
* APIs
* LLMs
* Embeddings
* Vector databases
* RAG

### Phase 7 — Integration

Combine the systems into an AI-assisted DevOps health platform.

---

# 🎯 Current Status

**Current phase:** Linux + Bash Health Checker

### Completed

* [x] Basic Bash script
* [x] Hostname information
* [x] User information
* [x] Date/time
* [x] Memory monitoring
* [x] Disk monitoring
* [x] Network information
* [x] Bash functions

### In progress

* [ ] Cron automation
* [ ] Health-check logging
* [ ] Git workflow
* [ ] GitLab repository

### Future

* [ ] Process monitoring
* [ ] Alerts
* [ ] CI/CD
* [ ] Docker
* [ ] Monitoring dashboard
* [ ] LLM integration
* [ ] RAG knowledge base
* [ ] AI-powered analysis
* [ ] AI DevOps assistant

---

# 💡 Project Philosophy

This project is intentionally designed to grow slowly.

The goal is **not** to build an AI system immediately.

The goal is to first understand the underlying DevOps concepts:

```text
Understand Linux
      ↓
Automate with Bash
      ↓
Schedule with Cron
      ↓
Track with Git
      ↓
Deploy with GitLab
      ↓
Monitor systems
      ↓
Learn AI
      ↓
Add LLM
      ↓
Add RAG
      ↓
Build AI DevOps Assistant
```

Each stage should be understood before moving to the next one.

---

## 🌱 Long-Term Goal

Build a practical AI-powered Linux/DevOps assistant that combines **system monitoring, automation, observability, LLMs, and RAG** to help engineers understand and troubleshoot infrastructure.

The project will evolve alongside my DevOps and AI learning journey.
