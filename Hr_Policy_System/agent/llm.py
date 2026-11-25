"""LLM factory: returns a chat model for the chosen provider."""
import os
import sys

# Allow running directly with the VS Code Play button
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Config.settings import GROQ_API_KEY, MISTRAL_API_KEY


def get_llm(provider: str = "groq"):
    """Return the configured LLM ('groq' or 'mistral').

    Provider packages are imported lazily, so you only need the one you use.
    """
    if provider == "mistral":
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is missing in .env")
        from langchain_mistralai.chat_models import ChatMistralAI

        return ChatMistralAI(
            model="mistral-small-latest",
            api_key=MISTRAL_API_KEY,
            temperature=0,
        )

    if provider != "groq":
        raise ValueError(f"Unknown provider '{provider}'. Use 'groq' or 'mistral'.")

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")
    from langchain_groq import ChatGroq

    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY,
        temperature=0,
    )


if __name__ == "__main__":
    llm = get_llm("groq")
    print(llm.invoke("Say 'LLM is connected!' in 4 words.").content)