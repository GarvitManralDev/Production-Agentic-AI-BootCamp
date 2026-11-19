# Production Agentic AI Engineering Bootcamp

My notes and code from Krish Naik's **Production Agentic AI Engineering Bootcamp**. Each module is a separate folder with its own Python environment, plus notebooks or runnable apps.

## Modules

| Module | Topic | Format | Status |
| --- | --- | --- | --- |
| [Module 3 - LangGraph](./Module%203%20-%20LangGraph%20/) | Building agents and chatbots with LangGraph | Jupyter notebooks | Done |
| [Module 4 - FastAPI](./Module%204%20-%20Fast%20API/) | Building production AI APIs with FastAPI | Runnable FastAPI apps | Done |

### Module 3 - LangGraph

| # | Notebook | What it covers |
| --- | --- | --- |
| 1 | [Basic ChatBot](./Module%203%20-%20LangGraph%20/1-BasicChatBot/1-basicChatBot.ipynb) | A simple chatbot built with the LangGraph Graph API (state, nodes, edges) |
| 2 | [ChatBot With Tool + ReAct](./Module%203%20-%20LangGraph%20/2-ChatBotWithTool+ReActConcept/2-ChatBotWithTool.ipynb) | Tool calling (Tavily search) and the ReAct agent pattern |
| 3 | [Memory + Streaming](./Module%203%20-%20LangGraph%20/3-ChatBot-Memorise+Streaming/3-ChatBoth-Memorise+Streaming.ipynb) | Checkpointer-based memory and the `stream()` / `astream()` modes |
| 4 | [Human in the Loop](./Module%203%20-%20LangGraph%20/4-HumanInTheLoop/humanintheloop.ipynb) | Pausing a graph with `interrupt()` and resuming it with `Command(resume=...)` |
| 5 | [Simple Multi-Agent Architecture](./Module%203%20-%20LangGraph%20/5-SimpleMultiAgentArchitecture/5-SimpleMutliAgentArchitecture.ipynb) | Multiple agents working together in one graph |

### Module 4 - FastAPI

Each section is a small FastAPI app you can run on localhost. Each section folder's README has the concept, a diagram and ready-to-run curl commands.

| # | Section | What it covers |
| --- | --- | --- |
| 1 | [Intro to FastAPI + CRUD](./Module%204%20-%20Fast%20API/01_intro_crud/) | Routes, path params, and POST / GET / PUT / PATCH / DELETE over an in-memory store |
| 2 | [Sync, Async & Background](./Module%204%20-%20Fast%20API/02_sync_async_background/) | Thread pool vs event loop, `asyncio.gather()`, `BackgroundTasks`, job polling |
| 3 | [Streaming with SSE](./Module%204%20-%20Fast%20API/03_streaming_sse/) | Streaming tokens, tool events and agent progress, with a browser UI |
| 4 | [WebSockets](./Module%204%20-%20Fast%20API/04_websockets/) | Two-way, real-time multi-turn agent chat, with a browser UI |
| 5 | [Typed APIs with Pydantic](./Module%204%20-%20Fast%20API/05_pydantic_models/) | Request validation, `Literal` types, custom validators, typed responses |
| 6 | [Auth & API Keys](./Module%204%20-%20Fast%20API/06_auth_api_keys/) | API key authentication (401) and role-based authorization (403) |
| 7 | [Rate Limits, Retries, Timeouts, Circuit Breakers](./Module%204%20-%20Fast%20API/07_resilience/) | Protecting the API from heavy users and failing LLM providers |
| 8 | [Idempotent LLM Requests](./Module%204%20-%20Fast%20API/08_idempotency/) | `Idempotency-Key` header so retries never run the LLM twice |
| 9 | [Secrets & Environment Config](./Module%204%20-%20Fast%20API/09_secrets_config/) | `pydantic-settings`, `.env`, `SecretStr`, failing fast on bad config |
| 10 | [**Capstone:** Production-Ready Streaming LLM API](./Module%204%20-%20Fast%20API/10_capstone_streaming_llm_api/) | Auth, rate limiting, validation, retry + timeout, idempotency, background logging and SSE in one app with a web UI |

## Tech Stack

- **Python** (3.13 with [uv](https://docs.astral.sh/uv/) for Module 3; 3.11+ with pip/conda for Module 4)
- **LangGraph** and **LangChain** for agent orchestration
- **Groq** (`langchain-groq`) for the LLM
- **Tavily** (`langchain-tavily`) for web search
- **LangSmith** for tracing
- **FastAPI**, **Uvicorn** and **Pydantic** for serving AI over HTTP, SSE and WebSockets
- **Jupyter** notebooks

## Getting Started

1. **Clone the repo**

   ```bash
   git clone git@github.com:GarvitManralDev/Production-Agentic-AI-BootCamp---Krish-Naik.git
   cd Production-Agentic-AI-BootCamp---Krish-Naik
   ```

2. **Set up the module you want to explore** (steps below).

`.env` files are git-ignored, so your keys stay out of the repo.

### Module 3 - LangGraph

```bash
cd "Module 3 - LangGraph "
uv sync                      # or: pip install -r requirements.txt
```

Create a `.env` file inside the module folder:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Open the notebooks in VS Code or Jupyter and select the module's `.venv` as the kernel.

### Module 4 - FastAPI

```bash
cd "Module 4 - Fast API"
pip install -r requirements.txt
cp 09_secrets_config/.env.example 09_secrets_config/.env                         # section 9
cp 10_capstone_streaming_llm_api/.env.example 10_capstone_streaming_llm_api/.env   # capstone

python 01_intro_crud/crud.py   # any section file works the same way
```

Then open <http://127.0.0.1:8080/docs>. Every app runs on port 8080, so stop one with `Ctrl+C` before starting the next.

## Getting API Keys

- Groq: <https://console.groq.com/keys>
- Tavily: <https://app.tavily.com/>
- LangSmith (optional): <https://smith.langchain.com/>
