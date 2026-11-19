"""
Section 4 - WebSockets for real-time agent applications

One long-lived, two-way connection. Client and server can both send at any time.

Message protocol (JSON):

    client -> server   {"message": "Book a meeting"}
    server -> client   {"type": "ack",      "text": "Message received!"}
                       {"type": "progress", "text": "AI is thinking..."}
                       {"type": "token",    "text": "Sure, "}
                       {"type": "final",    "text": "Sure, what time?"}
                       {"type": "error",    "text": "..."}

    GET /          -> browser chat UI
    WS  /ws/chat   -> the WebSocket endpoint

Run:   python 04_websockets/chat.py
Open:  http://127.0.0.1:8080  (open it in two tabs - each is its own session)
"""

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="WebSocket AI Chat")

# Seconds between server messages so progress is visible
STEP_DELAY = 0.5


def fake_agent_reply(message: str, history: list[str]) -> str:
    # A real app would call an LLM / LangGraph agent with the conversation history
    return f"(turn {len(history)}) AI answer for: {message}"


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    # Step 1: accept the connection
    await websocket.accept()

    # State lives as long as the connection - perfect for multi-turn conversations
    history: list[str] = []

    try:
        # Step 2: keep the connection open and handle messages in a loop
        while True:
            raw = await websocket.receive_text()

            try:
                message = json.loads(raw)["message"].strip()
                if not message:
                    raise ValueError
            except (json.JSONDecodeError, KeyError, TypeError, AttributeError, ValueError):
                await websocket.send_json(
                    {"type": "error", "text": 'Send JSON like {"message": "hi"}'}
                )
                continue

            history.append(message)

            # Step 3: push several updates for ONE user message
            await websocket.send_json({"type": "ack", "text": "Message received!"})

            await asyncio.sleep(STEP_DELAY)
            await websocket.send_json({"type": "progress", "text": "AI is thinking..."})

            reply = fake_agent_reply(message, history)
            for word in reply.split(" "):
                await asyncio.sleep(STEP_DELAY / 5)
                await websocket.send_json({"type": "token", "text": word + " "})

            await websocket.send_json({"type": "final", "text": reply})

    except WebSocketDisconnect:
        # Client closed the tab - clean up resources here
        print(f"Client disconnected after {len(history)} messages")


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>WebSocket AI Chat</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; }
    li { margin: 4px 0; }
    .you { font-weight: 600; }
    .progress, .ack, .system { color: #777; font-style: italic; }
    .error { color: #c0392b; }
  </style>
</head>
<body>
  <h2>WebSocket AI Chat</h2>
  <form onsubmit="sendMessage(); return false;">
    <input id="message" placeholder="Enter your message" autocomplete="off" />
    <button>Send</button>
  </form>
  <ul id="messages"></ul>

  <script>
    // Same host/port the page was served from
    const socket = new WebSocket(`ws://${location.host}/ws/chat`);
    let streaming = null;  // <li> currently receiving tokens

    function add(cls, text) {
      const li = document.createElement("li");
      li.className = cls;
      li.textContent = text;
      document.getElementById("messages").appendChild(li);
      return li;
    }

    socket.onopen = () => add("system", "Connected to AI server!");
    socket.onclose = () => add("system", "Disconnected.");

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "token") {
        if (!streaming) streaming = add("ai", "AI: ");
        streaming.textContent += msg.text;
      } else if (msg.type === "final") {
        streaming = null;
      } else {
        add(msg.type, msg.text);
      }
    };

    function sendMessage() {
      const input = document.getElementById("message");
      if (!input.value.trim()) return;
      socket.send(JSON.stringify({ message: input.value }));
      add("you", "You: " + input.value);
      input.value = "";
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
