# Production Agentic AI Engineering Bootcamp

My notes and code from Krish Naik's **Production Agentic AI Engineering Bootcamp**. Each module is a separate folder with its own Python environment and Jupyter notebooks.

## Modules

| Module | Topic | Status |
| --- | --- | --- |
| [Module 3 - LangGraph](./Module%203%20-%20LangGraph%20/) | Building agents and chatbots with LangGraph | Done |
| Module 4 - FastAPI | Serving agents behind an API | In progress |

### Module 3 - LangGraph

| # | Notebook | What it covers |
| --- | --- | --- |
| 1 | [Basic ChatBot](./Module%203%20-%20LangGraph%20/1-BasicChatBot/1-basicChatBot.ipynb) | A simple chatbot built with the LangGraph Graph API (state, nodes, edges) |
| 2 | [ChatBot With Tool + ReAct](./Module%203%20-%20LangGraph%20/2-ChatBotWithTool+ReActConcept/2-ChatBotWithTool.ipynb) | Tool calling (Tavily search) and the ReAct agent pattern |
| 3 | [Memory + Streaming](./Module%203%20-%20LangGraph%20/3-ChatBot-Memorise+Streaming/3-ChatBoth-Memorise+Streaming.ipynb) | Checkpointer-based memory and the `stream()` / `astream()` modes |
| 4 | [Human in the Loop](./Module%203%20-%20LangGraph%20/4-HumanInTheLoop/humanintheloop.ipynb) | Pausing a graph with `interrupt()` and resuming it with `Command(resume=...)` |
| 5 | [Simple Multi-Agent Architecture](./Module%203%20-%20LangGraph%20/5-SimpleMultiAgentArchitecture/5-SimpleMutliAgentArchitecture.ipynb) | Multiple agents working together in one graph |

## Tech Stack

- **Python 3.13**, managed with [uv](https://docs.astral.sh/uv/)
- **LangGraph** and **LangChain** for agent orchestration
- **Groq** (`langchain-groq`) for the LLM
- **Tavily** (`langchain-tavily`) for web search
- **LangSmith** for tracing
- **Jupyter** notebooks

## Getting Started

1. **Clone the repo**

   ```bash
   git clone git@github.com:GarvitManralDev/Production-Agentic-AI-BootCamp---Krish-Naik.git
   cd Production-Agentic-AI-BootCamp---Krish-Naik
   ```

2. **Install dependencies for a module**

   ```bash
   cd "Module 3 - LangGraph "
   uv sync
   ```

   Or with pip: `pip install -r requirements.txt`

3. **Add your API keys** in a `.env` file inside the module folder:

   ```env
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

   `.env` files are git-ignored, so your keys stay out of the repo.

4. **Run the notebooks** by opening them in VS Code or Jupyter and selecting the module's `.venv` as the kernel.

## Getting API Keys

- Groq: <https://console.groq.com/keys>
- Tavily: <https://app.tavily.com/>
- LangSmith (optional): <https://smith.langchain.com/>
