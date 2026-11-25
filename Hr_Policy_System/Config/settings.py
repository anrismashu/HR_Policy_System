import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
load_dotenv()

# Step up two levels: Config/settings.py -> Config/ -> Hr_Policy_System/
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CONFIG_DIR)

# File paths
DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "Data", "hr_policy_data_ai.txt")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Stage 1: Markdown Header Splitter configuration
HEADERS_TO_SPLIT_ON = [
    ("#", "section"),
    ("##", "subsection"),
    ("###", "question"),
]

# Stage 2: Recursive Character Splitter configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 120


