import os
import sys

# Allow running directly with the VS Code Play button
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.embeddings import JinaEmbeddings
from Config.settings import JINA_API_KEY


def get_embedding_model() -> JinaEmbeddings:
    """Initializes and returns the Jina embedding model."""
    if not JINA_API_KEY:
        raise ValueError("JINA_API_KEY is missing! Check your .env file.")

    return JinaEmbeddings(
        jina_api_key=JINA_API_KEY,
        model_name="jina-embeddings-v2-base-en",
    )


if __name__ == "__main__":
    embeddings = get_embedding_model()
    sample_vector = embeddings.embed_query("How many sick leave days do I get?")
    print(f"Embedding successful! Vector dimension: {len(sample_vector)}")