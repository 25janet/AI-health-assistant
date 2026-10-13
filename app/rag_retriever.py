
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

    # Extract the Markdown heading.
    heading_match = re.match(
        r"^#{1,6}\s+(.+)",
        content.strip()
    )
    heading = heading_match.group(1).lower() if heading_match else ""

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
    score += len((expanded_words - question_words) & heading_words) * 4

    # Give a small boost to actionable sections.
    if re.search(r"```(?:bash|shell)?", content_lower):
        score += 2

    query_terms = question_words | expanded_words

    # Determine the topic of the question.
    asks_oom = bool(query_terms & {
        "oom", "out-of-memory", "exhaustion", "event", "events"
    }) and "memory" in query_terms

    asks_process_memory = (
        "memory" in query_terms
        and bool(query_terms & {"process", "processes"})
    )

    asks_swap = bool(query_terms & {"swap", "swapon", "swapping"})

    asks_disk = bool(query_terms & {
        "disk", "filesystem", "storage", "space", "df", "directory"
    })

    asks_cpu = bool(query_terms & {
        "cpu", "processor", "processing", "load"
    })

    # Boost commands only when they match the question's topic.
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

        if "out-of-memory events" in heading:
            score -= 8

    if asks_swap and "swapon --show" in content_lower:
        score += 10

    if asks_disk and any(term in content_lower for term in (
        "df -h", "df -i", "du -", "docker system df"
    )):
        score += 8

    if asks_cpu and any(term in content_lower for term in (
        "top", "uptime", "mpstat", "iostat"
    )):
        score += 8

    # Prioritize the dedicated OOM section for OOM questions.
    normalized_heading = heading.replace("-", " ").replace("_", " ")

    if asks_oom and "out of memory" in normalized_heading:
        score += 15

    # Penalize introductory sections.
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