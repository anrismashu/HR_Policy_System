"""Streamlit UI for the HR Policy Assistant."""
import uuid

import streamlit as st

from agent.hr_agent import ask_hr_agent, build_hr_agent

PROVIDERS = ["groq"]  # add "mistral" back here once it works with your key
GREETING = "Hi there! I am your HR Policy Assistant. How can I help you today?"
EXAMPLES = [
    "How many days of annual leave do I get?",
    "What is the notice period after probation?",
    "How does the retirement match work?",
    "How do I raise a grievance?",
]

st.set_page_config(page_title="HR Policy Assistant", page_icon="💼", layout="centered")
st.title("💼 HR Policy Assistant")
st.caption("Ask about leave, working hours, benefits, or workplace rules. Answers come from the HR handbook.")


def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    st.session_state.thread_id = str(uuid.uuid4())


# --- Session state ---------------------------------------------------------
if "messages" not in st.session_state:
    reset_chat()
if "agents" not in st.session_state:
    st.session_state.agents = {}  # one agent per provider, so switching keeps its memory

# --- Sidebar ---------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    if len(PROVIDERS) > 1:
        provider = st.selectbox("LLM provider", PROVIDERS, index=0)
    else:
        provider = PROVIDERS[0]
    if st.button("🗑️ Clear chat & memory", use_container_width=True):
        reset_chat()
        st.rerun()

    st.divider()
    st.subheader("Try asking")
    for q in EXAMPLES:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q

    st.divider()
    st.caption("Topics: working hours, leave, insurance, probation, code of conduct.")

if provider not in st.session_state.agents:
    with st.spinner(f"Loading HR agent ({provider})..."):
        st.session_state.agents[provider] = build_hr_agent(provider=provider)

# --- Chat history ----------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- New input (typed or example button) -----------------------------------
user_query = st.chat_input("Ask an HR policy question...") or st.session_state.pop("pending", None)

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching HR handbook..."):
            try:
                answer = ask_hr_agent(
                    user_query,
                    agent=st.session_state.agents[provider],
                    thread_id=st.session_state.thread_id,
                )
            except Exception as e:
                if "429" in str(e) or "ratelimit" in type(e).__name__.lower():
                    answer = "The model provider is rate-limiting requests right now. Wait a few seconds and try again."
                else:
                    answer = f"Sorry, something went wrong while contacting the model ({type(e).__name__}). Please try again."
                st.error(answer)
                with st.expander("Technical details"):
                    st.code(str(e))
            else:
                st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})