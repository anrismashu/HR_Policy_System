import os
import re
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import JinaEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "Data", "hr_policy_data_ai.txt")

loader = TextLoader(DATA_FILE_PATH, encoding="utf-8")
document = loader.load()

# Get original text and normalize headings into Markdown
text = document[0].page_content
text = re.sub(r"(?m)^={5,}\s*$", "", text)
text = re.sub(r"(?m)^SECTION\s+(\d+):\s*(.+)$", r"# SECTION \1: \2", text)
text = re.sub(r"(?m)^(\d+\.\d+)\s+(.+)$", r"## \1 \2", text)
text = re.sub(r"(?m)^Q:\s*(.+)$", r"### Q: \1", text)

# STEP 1: Split using document structure
header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "section"),
        ("##", "subsection"),
        ("###", "question"),
    ],
    strip_headers=False,
)
structured_docs = header_splitter.split_text(text)

# STEP 2: Split oversized sections
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=120,
    add_start_index=True,
)
chunks = recursive_splitter.split_documents(structured_docs)

# STEP 3: Add source metadata
for chunk in chunks:
    chunk.metadata["source"] = DATA_FILE_PATH

# STEP 4: Build FAISS vector store with Jina Embeddings
embeddings_models = JinaEmbeddings(model_name="jina-embeddings-v2-base-en")
vector_store = FAISS.from_documents(chunks, embeddings_models)
print(f"Indexed {vector_store.index.ntotal} chunks into FAISS.")

# STEP 5: Define the tool and agent
@tool
def hr_search_policy(query: str) -> str:
    """Search the HR policy handbook for facts on leave, hours, benefits, and rules."""
    matches = vector_store.similarity_search(query, k=3)
    if not matches:
        return "No relevant policy information found in the database."
    
    return "\n\n---\n\n".join(
        f"[Section: {doc.metadata.get('subsection', doc.metadata.get('section', 'General'))}]\n{doc.page_content}"
        for doc in matches
    )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

agent = create_agent(
    model=llm,
    tools=[hr_search_policy],
    system_prompt=(
        "You are a helpful HR policy assistant. Always use the hr_search_policy tool "
        "to verify facts before answering. Rely strictly on the retrieved policy text; "
        "if a question is unrelated to the HR database or not covered in the text, "
        "refuse to answer and never guess."
    ),
)

if __name__ == "__main__":
    user_query = "hii who are you how are you what are you "
    print(f"\nUser: {user_query}")
    
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_query}]}
    )
    print("\nAgent:")
    print(response["messages"][-1].content)