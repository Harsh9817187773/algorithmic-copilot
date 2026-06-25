import streamlit as st
import time
import resource
from agent import agent_executor, system_message

# 1. CRITICAL FIX: This MUST be the first Streamlit command run!
st.set_page_config(page_title="Algorithmic Copilot", page_icon="🤖", layout="wide")

# 2. Now you can safely inject your Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0A0E17 0%, #111827 100%);
    }
    .stChatInput input {
        border-radius: 10px !important;
        border: 1px solid #1E293B !important;
        background-color: #131A26 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Algorithmic Copilot")
st.markdown("Paste your Codeforces problem below. The agent will write, compile, and test the C++ solution.")

# 3. Initialize the session state to remember chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display previous messages in the UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Handle user input
user_input = st.chat_input("Paste problem and Example Input/Output here...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Compiling and testing C++ code..."):
            try:
                # Track compilation start metrics
                start_time = time.perf_counter()
                
                # Trigger the LangGraph agent
                response = agent_executor.invoke({
                    "messages": [
                        ("system", system_message),
                        ("user", user_input)
                    ]
                }, config={"recursion_limit": 15})
                
                # Track post-execution metrics
                elapsed_time = time.perf_counter() - start_time
                iterations = sum(1 for m in response["messages"] if getattr(m, "name", "") == "execute_cpp_code")
                peak_memory_mb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / (1024 * 1024)
                
                # Display the Telemetry Metrics Rows
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric(label="Refactor Iterations", value=f"{iterations} loops", delta="-1 loop" if iterations > 1 else "Perfect Run")
                with m_col2:
                    st.metric(label="Compilation Speed", value=f"{elapsed_time:.2f}s")
                with m_col3:
                    st.metric(label="Peak System Memory", value=f"{peak_memory_mb:.2f} MB")
                
                # Extract the final answer
                final_content = response["messages"][-1].content
                if isinstance(final_content, list):
                    full_response = "".join([chunk["text"] for chunk in final_content if "text" in chunk])
                else:
                    full_response = final_content
                
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_msg = f"**Agent crashed or hit recursion limit:**\n\n`{str(e)}`"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})