# Autonomous Algorithmic Copilot

A local, RAG-powered AI agent designed to autonomously draft, compile, and debug C++ data structures for competitive programming.

## Architecture & Tech Stack
* **Orchestration:** LangGraph (Cyclical Reasoning/ReAct framework)
* **LLM Engine:** Meta Llama-3.3 via Groq (Optimized for high-speed, rate-limit-free inference)
* **Knowledge Base:** FAISS Vector Database & HuggingFace Embeddings (`all-MiniLM-L6-v2`)
* **Execution Environment:** Local sandboxed `g++` compilation via Python `subprocess`

## Key Engineering Features
1. **Local Tool Execution:** Engineered custom Python tools allowing the agent to write `.cpp` files to the local disk, pipe standard inputs (`stdin`) to the compiled binary, and read raw compiler standard errors (`stderr`).
2. **Provider Agnosticism:** Decoupled the logic loop from the LLM provider, migrating from Gemini to Groq/Llama-3 to bypass free-tier API rate limits and prevent rolling-window exhaustion.
3. **State Machine Failsafes:** Implemented strict graph recursion limits (`recursion_limit: 5`) to act as a circuit breaker, preventing infinite reasoning loops when the agent encounters unresolvable compilation errors.
4. **Retrieval-Augmented Generation (RAG):** Built a localized vector store to inject custom C++ data structure templates (e.g., Skew Heaps, Segment Trees) directly into the agent's context window on demand.