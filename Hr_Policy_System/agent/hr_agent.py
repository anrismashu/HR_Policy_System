"""HR Policy agent: a LangChain agent with a FAISS retrieval tool and per-thread memory."""
import os
import sys

# Allow running this file directly (e.g. VS Code Play button)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from agent.llm import get_llm
from agent.prompts import HR_SYSTEM_PROMPT
from agent.tools import search_hr_policy


def build_hr_agent(provider: str = "groq"):
    """Create the HR RAG agent. Conversation memory is kept per `thread_id`."""
    return create_agent(
        model=get_llm(provider=provider),
        tools=[search_hr_policy],
        system_prompt=HR_SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )


def _to_text(content) -> str:
    """Some providers (e.g. Mistral) return a list of content blocks instead of a string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        ).strip()
    return str(content)


def ask_hr_agent(question: str, agent=None, thread_id: str = "hr_session_1") -> str:
    """Send a question to the agent; history is preserved for the given thread_id."""
    if agent is None:
        agent = build_hr_agent()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return _to_text(result["messages"][-1].content)


if __name__ == "__main__":
    demo = build_hr_agent()
    print(ask_hr_agent("Hi, I am Ken!", agent=demo))
    print(ask_hr_agent("What is my name?", agent=demo))
