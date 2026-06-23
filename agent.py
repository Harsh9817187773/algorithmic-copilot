# agent.py
import os
from dotenv import load_dotenv

# Load the secret key from the hidden .env file
load_dotenv()
if not os.environ.get("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY not found. Please check your .env file.")

from langchain_groq import ChatGroq 
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from tools import execute_cpp_code

# 2. Initialize the Vector Store for database queries
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

@tool
def search_algorithm_docs(query: str) -> str:
    """Searches the local knowledge store for references on specific algorithms and data structures."""
    docs = vector_db.similarity_search(query, k=2)
    return "\n---\n".join([d.page_content for d in docs])

# 3. Swap the LLM Engine to Llama-3 running on Groq hardware
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

# 4. Consolidate the Agent's Tool Belt
tools = [search_algorithm_docs, execute_cpp_code]

# 5. Formulate the Agent's System Directive
system_message = (
    "You are an expert Competitive Programming Agent. Your job is to solve algorithmic issues.\n"
    "When given a problem instruction:\n"
    "1. Use search_algorithm_docs to fetch any structural references if needed.\n"
    "2. Write a comprehensive C++ solution including a main() function.\n"
    "3. ALWAYS test your solution by calling execute_cpp_code.\n"
    "4. CRITICAL: If the problem contains 'Example Input', you MUST pass that exact text into the `test_input` parameter of execute_cpp_code so the program does not hang waiting for cin.\n"
    "5. If you see a COMPILATION FAILED error, analyze the compiler output, fix your bugs, and call execute_cpp_code again.\n"
    "6. Do not stop until the code successfully runs.\n"
    "7. Once verified, print the complete final C++ code block and the exact terminal execution output."
)

# 6. Build the LangGraph workflow loop
agent_executor = create_react_agent(llm, tools)

# 7. Run a Local Terminal Execution Interface
if __name__ == "__main__":
    print("\n=== Algorithmic Copilot Terminal Initialize ===")
    print("Type 'exit' to quit at any time.\n")
    
    while True:
        print("User Question > (Paste your Codeforces problem below. Type 'SUBMIT' on a new line and press Enter to run it)")
        
        # Read multiple lines of pasted text until the user types SUBMIT
        lines = []
        while True:
            line = input()
            if line.strip().upper() == 'SUBMIT':
                break
            lines.append(line)
            
        user_input = "\n".join(lines)
        
        if user_input.strip().lower() == "exit":
            break
            
        print("\nAgent is working... (Processing thoughts and testing compilation tasks)")
        
        # Inject the system instructions directly into the message array
        response = agent_executor.invoke({
            "messages": [
                ("system", system_message),
                ("user", user_input)
            ]
        }, config={"recursion_limit": 15}) # <--- Our infinite loop breaker is still here!
        
        # Print out the final message from the conversation graph
        print("\n=== Copilot Final Response ===")
        final_content = response["messages"][-1].content
        
        if isinstance(final_content, list):
            full_response = ""
            for chunk in final_content:
                if isinstance(chunk, dict) and "text" in chunk:
                    full_response += chunk["text"]
            print(full_response)
        else:
            print(final_content)
            
        print("==============================\n")