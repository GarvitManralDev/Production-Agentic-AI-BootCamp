# 3. Streaming Tokens, Tool Events and Agent Progress with SSE

Don't leave users staring at a blank screen while the AI works.

```text
Without streaming:  Question → wait 15s ... → FULL RESPONSE
With streaming:     Machine → Machine learning → Machine learning is → ...
For agents:         Thinking... → Searching... → Calling tool... → Answer
```

**SSE (Server-Sent Events)** is a one-way, long-lived HTTP response (`text/event-stream`). The server keeps pushing events and the browser reads them with the built-in `EventSource`.

## Files

| File | What it shows |
| --- | --- |
| `token_stream.py` | Streams LLM tokens one by one (`token` events, then a `done` event) |
| `agent_stream.py` | Typed events (`status`, `tool_call`, `tool_result`, `token`, `done`), a browser UI, and stopping when the client disconnects |

## Run & try

```bash
python 03_streaming_sse/token_stream.py
curl -N "http://127.0.0.1:8080/stream?prompt=What%20is%20ML"
```

`-N` turns off curl's buffering so you see each event as it arrives.

```bash
python 03_streaming_sse/agent_stream.py
```

- **Browser:** open <http://127.0.0.1:8080>, type a question, and click **Ask**.
- **Terminal:** `curl -N "http://127.0.0.1:8080/agent-stream?question=LangGraph"`

## SSE wire format

```text
event: tool_call
data: {"tool": "web_search", "input": {"query": "LangGraph"}}

event: token
data: {"text": "Based "}

```

Each event is a set of `field: value` lines followed by a **blank line**.

## Understanding `yield`

```python
def normal():          # returns ONE final result
    return "Complete answer"

async def generator(): # produces values ONE BY ONE
    yield "Hello "
    yield "from "
    yield "AI"
```

`StreamingResponse` sends each yielded chunk to the client as soon as it's produced.

## Production tips

- Send the `Cache-Control: no-cache` and `X-Accel-Buffering: no` headers so proxies don't buffer the stream.
- Check `await request.is_disconnected()` and stop calling the LLM once the user is gone.
- Send JSON in `data:`, and name events so the frontend can tell them apart.
- `EventSource` reconnects automatically, so call `.close()` on the client when you get `done`.

> Streaming isn't only for LLM tokens. You can stream agent progress, tool events, workflow updates and the final output.
