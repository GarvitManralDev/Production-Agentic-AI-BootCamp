# 4. WebSockets for Real-Time Agent Applications

Use a **WebSocket** when the user and the AI need to talk **continuously in both directions**, without a new HTTP request for every message.

Good fits: voice agents, live assistants, AI interviewers, human-in-the-loop agents, customer-support bots.

## HTTP vs SSE vs WebSocket

```text
HTTP        Client → Server, Client ← Server, connection finished ❌
SSE         Client → Server, Client ← ← ← ← (server pushes, one direction)
WebSocket   Client ⇄ Server ⇄ Client ⇄ ... (open until someone closes it)
```

| | HTTP | SSE | WebSocket |
| --- | --- | --- | --- |
| Direction | request → response | server → client | both ways |
| Connection | closes after each response | open while streaming | open for the session |
| Best for | CRUD, one-shot LLM calls | token / progress streaming | chat, voice, interactive agents |

## Run & try

```bash
python 04_websockets/chat.py
```

- **Browser:** open <http://127.0.0.1:8080> and chat. Open a second tab to see that each connection keeps its own history.
- **Terminal:** use the `websockets` CLI, which comes with `uvicorn[standard]`:

  ```bash
  python -m websockets ws://127.0.0.1:8080/ws/chat
  > {"message": "Book a meeting tomorrow"}
  > {"message": "10 AM"}
  ```

## Server lifecycle

```text
await websocket.accept()           ← 1. accept the connection
while True:
    await websocket.receive_text() ← 2. wait for the user
    await websocket.send_json(...) ← 3. push ack / progress / tokens / final
except WebSocketDisconnect:        ← 4. user left → clean up
```

## Production tips

- Wrap the loop in `try/except WebSocketDisconnect`. Otherwise every closed tab logs a stack trace.
- Agree on a **JSON message protocol** with a `type` field instead of sending plain strings.
- Validate every incoming message. A bad message should get an `error` reply, not kill the connection.
- Per-connection state (like `history`) lives in memory. To scale to many servers you need sticky sessions or a shared store such as Redis.
- Authenticate during the handshake, using a query token or cookie, **before** calling `accept()`.

> WebSocket keeps the connection open, so the user and the agent can keep talking in both directions.
