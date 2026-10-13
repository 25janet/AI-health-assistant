
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
        "networking", "connectivity", "interface"
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

    # Extract the Markdown heading when one exists.
    heading_match = re.match(
        r"^#{1,6}\s+(.+)",
        content.strip()
    )

    heading = heading_match.group(1).lower() if heading_match else ""

    content_words = tokenize(content)
    heading_words = tokenize(heading)

    # Direct matches matter more than expanded synonyms.
    direct_matches = question_words & content_words
    expanded_matches = expanded_words & content_words

    score = (
        len(direct_matches) * 3
        + len(expanded_matches - question_words)
    )

    # Give relevant headings more weight than body text.
    score += len(question_words & heading_words) * 5
    score += len((expanded_words - question_words) & heading_words) * 3

    # Prefer actionable diagnostic sections.
    has_commands = bool(
        re.search(r"```(?:bash|shell)?", content_lower)
    )

    if has_commands:
        score += 2

    # Boost sections containing useful diagnostic commands.
    diagnostic_commands = (
        "df -h",
        "df -i",
        "du -",
        "docker system df",
        "journalctl --disk-usage",
        "free -h",
        "vmstat",
        "ps aux",
        "swapon --show",
        "journalctl -k",
        "top",
        "uptime",
        "mpstat",
        "iostat",
        "ip addr",
        "ip route",
        "systemctl status",
    )

    if any(command in content_lower for command in diagnostic_commands):
        score += 3

    # Detect questions about out-of-memory events.
    query_terms = question_words | expanded_words

    asks_about_oom = (
        bool(query_terms & {
            "oom", "out-of-memory", "exhaustion"
        })
        or (
            "memory" in query_terms
            and bool(query_terms & {
                "event", "events", "incident", "occurrence",
                "killed", "kill"
            })
        )
    )

    # Normalize the heading so hyphenated phrases can match.
    normalized_heading = (
        heading.replace("-", " ").replace("_", " ")
    )

    is_oom_heading = (
        "out of memory" in normalized_heading
        or "oom" in heading_words
    )

    # Strongly prioritize the dedicated OOM section.
    if asks_about_oom and is_oom_heading:
        score += 15

    # Boost relevant kernel logs and OOM evidence.
    oom_evidence = (
        "journalctl -k",
        "oom-kill",
        "oom killer",
        "killed process",
        "out of memory",
    )

    if asks_about_oom and any(
        term in content_lower for term in oom_evidence
    ):
        score += 5

    # Avoid introductory sections dominating search results.
    if heading.startswith(("purpose", "introduction")):
        score -= 5

    if heading.startswith("symptoms"):
        score -= 2

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