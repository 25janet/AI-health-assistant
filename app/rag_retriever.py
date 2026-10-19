
# ============================================================
# Local RAG Retriever
# ============================================================

from pathlib import Path
import re


# ------------------------------------------------------------
# 1. Locate the local knowledge base
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE_DIR = PROJECT_DIR / "knowledge_base" / "runbooks"


# ------------------------------------------------------------
# 2. Load and split Markdown documents into sections
# ------------------------------------------------------------

def load_and_chunk_documents():
    chunks = []

    if not KNOWLEDGE_BASE_DIR.exists():
        print(f"Knowledge base not found: {KNOWLEDGE_BASE_DIR}")
        return chunks

    for document_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        content = document_path.read_text(encoding="utf-8")

        # Split the document at Markdown headings.
        sections = re.split(
            r"(?m)(?=^#{1,6}\s+)",
            content
        )

        for section in sections:
            section = section.strip()

            if not section:
                continue

            chunks.append({
                "source": document_path.name,
                "content": section
            })

    return chunks


# ------------------------------------------------------------
# 3. Convert text into searchable words
# ------------------------------------------------------------

def tokenize(text):
    return set(
        re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
    )


STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "do", "does",
    "how", "what", "when", "where", "why", "which",
    "i", "me", "my", "we", "our", "you", "your",
    "to", "of", "in", "on", "for", "and", "or", "it",
    "can", "could", "should", "would", "with", "from",
    "about", "check", "please", "tell", "show",
    "if", "whether", "using", "use", "too"
}


# ------------------------------------------------------------
# 4. Expand common troubleshooting terms
# ------------------------------------------------------------

SYNONYMS = {
    "investigate": {
        "diagnose", "inspect", "troubleshoot", "identify"
    },
    "diagnose": {
        "investigate", "inspect", "troubleshoot"
    },
    "troubleshoot": {
        "investigate", "diagnose", "inspect"
    },
    "high": {
        "full", "critical", "excessive", "heavy"
    },
    "disk": {
        "filesystem", "storage", "space"
    },
    "usage": {
        "consumption", "utilization", "space"
    },
    "docker": {
        "container", "containers", "image", "images",
        "volume", "volumes", "cache"
    },
    "logs": {
        "logging", "journal", "journalctl"
    },
    "oom": {
        "out", "of", "memory", "out-of-memory",
        "exhaustion", "event", "events"
    },
    "out-of-memory": {
        "oom", "memory", "exhaustion", "event", "events"
    },
    "exhaustion": {
        "oom", "out-of-memory", "memory"
    },
    "event": {
        "events", "incident", "occurrence"
    },
    "events": {
        "event", "incident", "occurrence"
    },
    "memory": {
        "ram", "oom", "out-of-memory"
    },
    "ram": {
        "memory", "oom"
    },
    "swap": {
        "swapon", "swapping"
    },
    "cpu": {
        "processor", "processing"
    },
    "network": {
        "networking", "connectivity", "interface",
        "ip", "route", "gateway", "firewall"
    },
    "networking": {
        "network", "connectivity", "interface"
    },
    "interface": {
        "interfaces", "link", "device"
    },
    "connectivity": {
        "network", "networking", "connection", "ping"
    },
    "firewall": {
        "iptables", "nft", "traffic", "filtering"
    },
    "gateway": {
        "route", "routing", "default"
    },
    "service": {
        "systemd", "daemon", "services"
    },
    "services": {
        "service", "systemd", "daemon"
    },
}


def expand_query(question):
    words = tokenize(question) - STOP_WORDS
    expanded_words = set(words)

    for word in words:
        expanded_words.update(SYNONYMS.get(word, set()))

    return words, expanded_words


# ------------------------------------------------------------
# 5. Score how relevant each section is to a question
# ------------------------------------------------------------

def score_chunk(question_words, expanded_words, chunk):
    content = chunk["content"]
    content_lower = content.lower()

    # Extract the Markdown heading.
    heading_match = re.match(
        r"^#{1,6}\s+(.+)",
        content.strip()
    )

    heading = (
        heading_match.group(1).lower()
        if heading_match
        else ""
    )

    heading_lower = heading.lower()

    content_words = tokenize(content)
    heading_words = tokenize(heading)

    # Score direct matches and expanded synonyms.
    direct_matches = question_words & content_words
    expanded_matches = expanded_words & content_words

    score = (
        len(direct_matches) * 3
        + len(expanded_matches - question_words)
    )

    # Headings are stronger relevance signals than body text.
    score += len(question_words & heading_words) * 6
    score += len(
        (expanded_words - question_words) & heading_words
    ) * 4

    # Give a small boost to actionable sections.
    if re.search(r"```(?:bash|shell)?", content_lower):
        score += 2

    query_terms = question_words | expanded_words

    # Determine the topic of the question.
    asks_oom = (
        bool(query_terms & {
            "oom", "out-of-memory", "exhaustion", "event", "events"
        })
        and "memory" in query_terms
    )

    asks_process_memory = (
        "memory" in query_terms
        and bool(query_terms & {"process", "processes"})
    )

    asks_swap = bool(
        query_terms & {"swap", "swapon", "swapping"}
    )

    asks_disk = bool(
        query_terms & {
            "disk", "filesystem", "storage", "space",
            "df", "directory"
        }
    )

    asks_cpu = bool(
        query_terms & {"cpu", "processor", "processing", "load"}
    )

    # Use the full question for intent-specific matching.
    question_lower = " ".join(question_words).lower()

    # --------------------------------------------------------
    # Memory troubleshooting
    # --------------------------------------------------------

    if asks_oom and any(term in content_lower for term in (
        "journalctl -k",
        "oom-kill",
        "killed process",
        "out of memory",
    )):
        score += 8

    if asks_process_memory:
        if "ps aux --sort=-%mem" in content_lower:
            score += 15

        if "out-of-memory events" in heading_lower:
            score -= 8

    if asks_swap and "swapon --show" in content_lower:
        score += 10

    # --------------------------------------------------------
    # Disk troubleshooting
    # --------------------------------------------------------

    if asks_disk and any(term in content_lower for term in (
        "df -h",
        "df -i",
        "du -",
        "docker system df",
    )):
        score += 8

    # --------------------------------------------------------
    # CPU troubleshooting
    # --------------------------------------------------------

    if asks_cpu:
        # Per-core CPU monitoring.
        if any(term in question_lower for term in (
            "individual cores",
            "per core",
            "each core",
            "individual cpu",
        )):
            if any(term in content_lower for term in (
                "per-cpu",
                "individual cpu",
                "mpstat -p all",
            )):
                score += 18

        # systemd service troubleshooting.
        if (
            "systemd service" in question_lower
            or "service causing" in question_lower
        ):
            if "systemctl status" in content_lower:
                score += 18

            if "journalctl" in content_lower:
                score += 10

        # CPU troubleshooting through logs.
        if (
            "linux logs" in question_lower
            or "using linux logs" in question_lower
        ):
            if "journalctl" in content_lower:
                score += 18

        # Distinguish memory pressure from disk I/O.
        if (
            "memory or disk i/o" in question_lower
            or "disk i/o" in question_lower
        ):
            if "vmstat" in content_lower:
                score += 14

            if "wa" in content_lower or "i/o" in content_lower:
                score += 8

        # Excessive CPU consumption by a process.
        if (
            "too much cpu" in question_lower
            or "process is using" in question_lower
        ):
            if "ps aux --sort=-%cpu" in content_lower:
                score += 18

            if (
                "corrective actions" in content_lower
                or "safe corrective actions" in content_lower
            ):
                score += 8

        # Verify that the CPU problem has been resolved.
        if (
            "verify" in question_lower
            and (
                "resolved" in question_lower
                or "problem" in question_lower
            )
        ):
            if "## 11. verification" in content_lower:
                score += 30

    # --------------------------------------------------------
    # Networking troubleshooting
    # --------------------------------------------------------

    asks_network_interface = (
        "interface" in query_terms
        and bool(query_terms & {"up", "link", "status"})
    )

    asks_missing_ip = (
        bool(query_terms & {"missing", "incorrect", "configuration"})
        and bool(query_terms & {"ip", "address", "network"})
    )

    asks_default_route = (
        "default route" in question_lower
        or "incorrect gateway" in question_lower
        or (
            "gateway" in query_terms
            and "route" in query_terms
        )
    )

    asks_firewall = (
        "firewall" in query_terms
        and bool(query_terms & {
            "blocking", "traffic", "iptables", "nft"
        })
    )

    asks_network_logs = (
        "network" in query_terms
        and "logs" in query_terms
    )

    asks_network_verification = (
        "verify" in query_terms
        and bool(query_terms & {
            "resolved", "resolution", "problem"
        })
        and (
            "network" in query_terms
            or "networking" in query_terms
        )
    )

    asks_tcp_port = (
        bool(query_terms & {"tcp", "remote"})
        and bool(query_terms & {"port", "reachable", "reachability"})
    )

    asks_listening_port = (
        "listening" in query_terms
        and "port" in query_terms
    )

    asks_dns = (
        "dns" in query_terms
        or "resolution" in query_terms
        or "resolving" in query_terms
    )

    # Network interface status.
    if asks_network_interface:
        if "ip link show" in content_lower:
            score += 18

        if "ip -br addr" in content_lower:
            score += 8

    # Missing IP address or incorrect interface configuration.
    # Missing IP address or incorrect interface configuration.
    if asks_missing_ip:
        # Strongly prioritize the section that explains
        # how to inspect interface addresses.
        if "ip -br addr" in content_lower:
            score += 30

        if "ip addr show" in content_lower:
            score += 20

        # The routing section is useful as a secondary check,
        # but should not outrank interface inspection.
        if "ip route show" in content_lower:
            score += 3

        # Verification is useful after making a correction,
        # not as the primary diagnostic procedure.
        if "## 12. verification" in content_lower:
            score -= 15
    # Default route and gateway.
    if asks_default_route:
        if "ip route show" in content_lower:
            score += 18

        if "ip route get" in content_lower:
            score += 10

    # Firewall rules.
    if asks_firewall:
        if "nft list ruleset" in content_lower:
            score += 18

        if "iptables -l -n -v" in content_lower:
            score += 12

    # Network-related logs.
    if asks_network_logs:
        if "journalctl" in content_lower:
            score += 12

        if "journalctl -k" in content_lower:
            score += 6

        if "systemctl status" in content_lower:
            score += 5

    # Verify resolution of a networking problem.
    if asks_network_verification:
        if "## 12. verification" in content_lower:
            score += 25

        if "verification" in heading_lower:
            score += 12

    # Test whether a remote TCP port is reachable.
    if asks_tcp_port:
        if "nc -vz" in content_lower:
            score += 20

    # Check whether a service is listening on a port.
    if asks_listening_port:
        if "ss -tulpn" in content_lower:
            score += 20

        if "ss -ltnp" in content_lower:
            score += 15

    # DNS resolution troubleshooting.
    if asks_dns:
        if "getent hosts" in content_lower:
            score += 18

        if "resolvectl status" in content_lower:
            score += 10

        if "/etc/resolv.conf" in content_lower:
            score += 8

    # Connectivity tests should favor the connectivity section.
    asks_connectivity = (
        "connectivity" in query_terms
        or "ping" in query_terms
        or "internet" in query_terms
    )

    if asks_connectivity:
        if "ping -c 4" in content_lower:
            score += 10

    # --------------------------------------------------------
    # General prioritization and penalties
    # --------------------------------------------------------

    # Prioritize the dedicated OOM section for OOM questions.
    normalized_heading = heading.replace("-", " ").replace("_", " ")

    if asks_oom and "out of memory" in normalized_heading:
        score += 15

    # Penalize introductory sections.
    if heading.startswith(("purpose", "introduction")):
        score -= 5

    # Reduce the score of generic symptoms sections.
    if heading.startswith("symptoms"):
        score -= 2

    # Summary tables mention many topics but often lack detailed procedures.
    if "troubleshooting summary" in heading_lower:
        score -= 12

    return score


# ------------------------------------------------------------
# 6. Retrieve the most relevant sections
# ------------------------------------------------------------

def retrieve_chunks(question, chunks, top_k=3):
    question_words, expanded_words = expand_query(question)

    if not question_words:
        return []

    scored_chunks = []

    for chunk in chunks:
        score = score_chunk(
            question_words,
            expanded_words,
            chunk
        )

        if score > 0:
            scored_chunks.append({
                "source": chunk["source"],
                "content": chunk["content"],
                "score": score
            })

    # Highest-scoring sections come first.
    scored_chunks.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scored_chunks[:top_k]


# ------------------------------------------------------------
# 7. Run the retriever interactively
# ------------------------------------------------------------

if __name__ == "__main__":
    document_chunks = load_and_chunk_documents()

    print(f"\nKnowledge base: {KNOWLEDGE_BASE_DIR}")
    print(f"Loaded {len(document_chunks)} chunks.")

    if not document_chunks:
        print("No Markdown runbooks were loaded.")
        raise SystemExit(1)

    print("\nAsk a question about Linux troubleshooting.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Question: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nRetriever stopped.")
            break

        if question.lower() == "exit":
            print("\nRetriever stopped.")
            break

        if not question:
            continue

        results = retrieve_chunks(
            question,
            document_chunks,
            top_k=3
        )

        if not results:
            print("\nNo matching chunks found.\n")
            continue

        print("\nRetrieved chunks:\n")

        for index, result in enumerate(results, start=1):
            print(
                f"Result {index} | "
                f"Score: {result['score']}"
            )
            print(f"Source: {result['source']}")
            print("-" * 60)
            print(result["content"])
            print("-" * 60)

        print()
