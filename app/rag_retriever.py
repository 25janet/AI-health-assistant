
# ============================================================
# RAG Retriever
# ============================================================

from pathlib import Path
import re


# ------------------------------------------------------------
# 1. Define the knowledge base directory
# ------------------------------------------------------------

KNOWLEDGE_BASE_DIR = Path("knowledge_base/runbooks")


# ------------------------------------------------------------
# 2. Read Markdown runbooks and split them into chunks
# ------------------------------------------------------------

def load_and_chunk_documents():
    chunks = []

    for document_path in KNOWLEDGE_BASE_DIR.glob("*.md"):
        content = document_path.read_text(encoding="utf-8")

        # Split the document at Markdown headings.
        sections = re.split(r"(?m)(?=^#{1,6}\s+)", content)

        for section in sections:
            section = section.strip()

            if not section:
                continue

            # Store the text and its source for later citation.
            chunks.append({
                "source": document_path.name,
                "content": section
            })

    return chunks


# ------------------------------------------------------------
# 3. Run a simple inspection test
# ------------------------------------------------------------

if __name__ == "__main__":
    document_chunks = load_and_chunk_documents()

    print(f"\nDocuments directory: {KNOWLEDGE_BASE_DIR}")
    print(f"Chunks loaded: {len(document_chunks)}\n")

    for index, chunk in enumerate(document_chunks, start=1):
        print("=" * 60)
        print(f"Chunk {index}")
        print(f"Source: {chunk['source']}")
        print("-" * 60)
        print(chunk["content"][:500])
        print()

