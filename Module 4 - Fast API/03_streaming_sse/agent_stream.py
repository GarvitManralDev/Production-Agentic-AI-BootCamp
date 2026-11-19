"""
Section 3.2 - Streaming agent progress, tool events and tokens with SSE

One stream, several event types - the client decides how to render each:

    status       {"step": "Understanding your question..."}
    tool_call    {"tool": "web_search", "input": {...}}
    tool_result  {"tool": "web_search", "output": "..."}
    token        {"text": "..."}
    done         {"elapsed_seconds": 3.1}

    GET /               -> small browser UI (EventSource) to watch the stream live
    GET /agent-stream   -> the SSE endpoint

Run:   python 03_streaming_sse/agent_stream.py
Open:  http://127.0.0.1:8080
"""

import asyncio
import json
import time
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(title="SSE Agent Progress Streaming")

# Seconds between events so progress is visible
STEP_DELAY = 0.6


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def run_agent(question: str, request: Request) -> AsyncIterator[str]:
    start = time.perf_counter()

    async def emit(event: str, data: dict) -> str:
        await asyncio.sleep(STEP_DELAY)
        return sse(event, data)

    yield await emit("status", {"step": "Understanding your question..."})
    yield await emit("status", {"step": "Planning which tool to use..."})

    yield await emit("tool_call", {"tool": "web_search", "input": {"query": question}})
    yield await emit(
        "tool_result",
        {"tool": "web_search", "output": f"3 articles found about '{question}'"},
    )

    yield await emit("status", {"step": "Writing the final answer..."})

    answer = f"Based on 3 sources, here is a short answer about {question}."
    for word in answer.split(" "):
        # Stop work if the user closed the tab - don't waste LLM tokens
        if await request.is_disconnected():
            print("Client disconnected, stopping agent")
            return
        await asyncio.sleep(STEP_DELAY / 4)
        yield sse("token", {"text": word + " "})

    yield sse("done", {"elapsed_seconds": round(time.perf_counter() - start, 2)})


@app.get("/agent-stream")
async def agent_stream(request: Request, question: str = "FastAPI"):
    return StreamingResponse(
        run_agent(question, request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>SSE Agent Stream</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; }
    #log li { margin: 4px 0; }
    .status { color: #555; }
    .tool_call, .tool_result { color: #7a3fb8; font-family: monospace; }
    #answer { padding: 12px; background: #f3f3f3; border-radius: 8px; min-height: 1.5em; }
  </style>
</head>
<body>
  <h2>Agent progress over SSE</h2>
  <input id="q" value="FastAPI" />
  <button onclick="start()">Ask</button>
  <ul id="log"></ul>
  <div id="answer"></div>

  <script>
    let source;

    function add(cls, text) {
      const li = document.createElement("li");
      li.className = cls;
      li.textContent = text;
      document.getElementById("log").appendChild(li);
    }

    function start() {
      if (source) source.close();
      document.getElementById("log").innerHTML = "";
      document.getElementById("answer").textContent = "";

      const q = encodeURIComponent(document.getElementById("q").value);
      source = new EventSource(`/agent-stream?question=${q}`);

      source.addEventListener("status", e => add("status", "⏳ " + JSON.parse(e.data).step));
      source.addEventListener("tool_call", e => add("tool_call", "🔧 call " + e.data));
      source.addEventListener("tool_result", e => add("tool_result", "📦 result " + e.data));
      source.addEventListener("token", e => {
        document.getElementById("answer").textContent += JSON.parse(e.data).text;
      });
      source.addEventListener("done", e => {
        add("status", "✅ done " + e.data);
        source.close();  // otherwise EventSource auto-reconnects
      });
    }
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
