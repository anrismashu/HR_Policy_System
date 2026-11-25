import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import TextLoader
from Config.settings import DATA_FILE_PATH

def load_hr_document(file_path: str = DATA_FILE_PATH) -> str:
    """Loads the HR policy text file and returns its raw string content."""
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    return documents[0].page_content
