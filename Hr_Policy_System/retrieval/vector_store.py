"""Build, save and load the FAISS index over the HR handbook.

Usage:
    python -m retrieval.vector_store            # load (or build if missing) and test a query
    python -m retrieval.vector_store --rebuild  # re-embed the handbook and overwrite the index
"""
import argparse
import os
import sys

# Allow running directly with the VS Code Play button
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import FAISS

from Config.settings import PROJECT_ROOT
from ingestion.splitter import get_hr_chunks
from retrieval.embeddings import get_embedding_model

FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "faiss_hr_index")
FAISS_INDEX_FILE = os.path.join(FAISS_INDEX_PATH, "index.faiss")


def build_or_load_vector_store(force_rebuild: bool = False) -> FAISS:
    """Load the FAISS index from disk, or build and save it if missing."""
    embeddings = get_embedding_model()

    if os.path.exists(FAISS_INDEX_FILE) and not force_rebuild:
        # FAISS stores chunk metadata as a pickle, so only load indexes you built yourself.
        return FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    chunks = get_hr_chunks()
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    return vector_store


def get_retriever(k: int = 3):
    """Return a LangChain retriever that yields the top-k matching chunks."""
    return build_or_load_vector_store().as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build or test the HR FAISS index")
    parser.add_argument("--rebuild", action="store_true", help="re-embed and overwrite the index")
    parser.add_argument("--query", default="What is the probation period?")
    args = parser.parse_args()

    if args.rebuild:
        store = build_or_load_vector_store(force_rebuild=True)
        print(f"Rebuilt index with {store.index.ntotal} chunks.")

    results = get_retriever(k=2).invoke(args.query)
    print(f"Retrieved {len(results)} chunks for: {args.query!r}\n")
    for i, doc in enumerate(results, 1):
        print(f"--- Result {i} ---")
        print("Metadata:", doc.metadata)
        print(doc.page_content[:300], "\n")
