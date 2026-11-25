import os
import sys

# Allow running this file directly with the VS Code Play button
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from Config.settings import (
    HEADERS_TO_SPLIT_ON,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DATA_FILE_PATH,
)
from ingestion.loader import load_hr_document
from ingestion.preprocessor import preprocess_text

def split_hr_document(cleaned_text: str, source_path: str = DATA_FILE_PATH) -> list:
    """Splits Markdown-formatted HR text by headers first, then by character size."""
    # Stage 1: Split by document structure (#, ##, ###)
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    structured_docs = header_splitter.split_text(cleaned_text)
    # Stage 2: Split any oversized sections by character limit
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )
    chunks = recursive_splitter.split_documents(structured_docs)
    # Stage 3: Attach source metadata to every chunk
    for chunk in chunks:
        chunk.metadata["source"] = os.path.basename(source_path)
    return chunks

def get_hr_chunks() -> list:
    """Helper function that runs the full ingestion chain and returns ready chunks."""
    raw_text = load_hr_document()
    cleaned_text = preprocess_text(raw_text)
    return split_hr_document(cleaned_text)

if __name__ == "__main__":
    chunks = get_hr_chunks()
    print("Total chunks:", len(chunks))
    print("\n--- First Chunk ---")
    print("Metadata:", chunks[0].metadata)
    print("Content:\n", chunks[0].page_content)
    print("\n--- Second Chunk ---")
    print("Metadata:", chunks[1].metadata)
    print("Content:\n", chunks[1].page_content)