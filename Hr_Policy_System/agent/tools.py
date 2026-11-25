"""Retrieval tool the agent calls to search the HR handbook."""
import logging
import os
import sys
from functools import lru_cache

# Allow running directly with the VS Code Play button
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool

from retrieval.vector_store import get_retriever

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_cached_retriever():
    """Load the retriever on first use (not at import time) so the app starts fast."""
    return get_retriever(k=3)


@tool
def search_hr_policy(query: str) -> str:
    """Search the company HR policy handbook for rules on leave, working hours, benefits, conduct, and procedures."""
    try:
        docs = _get_cached_retriever().invoke(query)
    except Exception as e:  # e.g. embedding API down, index missing, faiss not installed
        logger.exception("HR handbook search failed")  # full traceback goes to the terminal
        return (
            f"ERROR: the HR handbook could not be searched ({type(e).__name__}). "
            "Do NOT answer from your own knowledge and do NOT invent policy details or sources. "
            "Tell the user the handbook is temporarily unavailable and suggest contacting HR."
        )

    if not docs:
        return "No matching HR policy sections found."

    formatted_chunks = []
    for i, doc in enumerate(docs, 1):
        section = doc.metadata.get("section", "General")
        subsection = doc.metadata.get("subsection", "")
        header_info = f"{section} | {subsection}".strip(" |")
        formatted_chunks.append(f"[Chunk {i} - {header_info}]\n{doc.page_content}")

    return "\n\n".join(formatted_chunks)


if __name__ == "__main__":
    print(search_hr_policy.invoke("How does overtime pay work?"))   