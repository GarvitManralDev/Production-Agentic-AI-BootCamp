# Building Production AI APIs with FastAPI

 FastAPI is a modern, high-performance web framework used for building RESTful APIs with Python 3.8+. It is heavily relied upon by developers for its speed, simplicity, and reliance on standard Python type hints.

---

# Basic Setup

## Install

```bash
pip install fastapi uvicorn
```



## FastAPI Docs:

https://fastapi.tiangolo.com/


## Run

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# 1. Designing Synchronous, Asynchronous, and Background AI Workloads

## Goal

Understand **how our API should execute different types of work without unnecessarily making users wait or blocking the server.**

LLM calls can be slow. If hundreds of users send requests at the same time, we do not want the application to inefficiently wait for one request after another.

Think:

```text
Synchronous   → Finish this work before continuing.

Asynchronous  → While waiting, allow other work to happen.

Background    → Send the response first, do secondary work afterward.
```

---

## 1.1 Synchronous Example

### Problem

A normal synchronous function waits until its work is finished before continuing.



### Mental Model

```text
Request
   ↓
Start function
   ↓
time.sleep(5)
   ↓
WAIT
   ↓
Continue
   ↓
Return response
```



> **Synchronous means we perform one operation and wait for it to complete before continuing.**

---

## 1.2 Asynchronous Example

### Goal

Use waiting time more efficiently when calling external services such as LLMs, databases, vector databases, or APIs.



### Mental Model

```text
User A
   ↓
Call LLM
   ↓
Waiting...
            Server handles User B
            Server handles User C
   ↓
LLM responds
   ↓
Continue User A
```

### Why Important for AI?

AI applications constantly wait for:

```text
LLM APIs
Vector databases
SQL databases
Web searches
Agent tools
External APIs
Cloud services
```



> **Async does not magically make the LLM faster. It helps our server use its waiting time more efficiently.**

---

## 1.3 Background Task Example

### Problem

After generating an answer, we may also want to:

```text
Save logs
Store analytics
Send an email
Save conversation history
```

The user does not necessarily need to wait for those secondary operations.



### Mental Model

```text
Generate answer
      ↓
Return response
      ↓
User receives answer
      ↓
Save log afterward
```

### Takeaway

```text
Sync       → Do it and wait.

Async      → Wait efficiently.

Background → User does not need to wait for it.
```

---





# 2. Streaming Tokens, Tool Events, and Agent Progress with SSE

## Goal

Do not make users stare at a blank screen while the AI is working.

Without streaming:

```text
Question
   ↓
Wait 15 seconds...
   ↓
FULL RESPONSE
```

With streaming:

```text
Machine
Machine learning
Machine learning is
Machine learning is a...
```

For agents, we may stream progress:

```text
Thinking...
Searching...
Calling tool...
Analyzing...
Generating answer...
```

SSE means **Server-Sent Events**. It allows the server to continuously send updates to the client.

---



## Understanding `yield`

Normal function:

```python
def normal_function():

    return "Complete answer"
```

Returns one final result.

Generator:

```python
def generator():

    yield "Hello "
    yield "from "
    yield "AI"
```

Produces values one by one.

---



### Takeaway

> **Streaming is not only for LLM tokens. We can stream agent progress, tool events, workflow updates, and final output.**

---




# 3. Supporting WebSockets for Real-Time Agent Applications

## Goal

Use **WebSocket** when the **user and AI need to communicate continuously in both directions** without creating a new HTTP request every time.

WebSocket is especially useful for:

- Voice Agents
- Live AI Assistants
- Interactive AI Agents
- AI Interviewers
- Human-in-the-loop Systems
- Real-time AI Applications

---

## Why Do We Need WebSocket?

The easiest way to understand WebSocket is to compare it with a normal HTTP request.

Imagine you are building an **AI assistant**.

The user sends:

```text
Hello
```

The AI responds:

```text
Hi! How can I help you?
```

With normal HTTP:

```text
Client → Server
Client ← Server

Connection Finished ❌
```

If the user wants to ask another question, another HTTP request is required.

```text
User → "Explain RAG"

AI → "RAG stands for Retrieval-Augmented Generation."

Connection Finished ❌
```

So the pattern is:

```text
Request
   ↓
Response
   ↓
Finished
```

This works perfectly for many AI applications.

But what if we are building something highly interactive?

For example:

```text
Voice Agent
Live AI Assistant
AI Interviewer
Customer Support Agent
Human-in-the-loop Agent
```

In these applications, we may want the user and AI to communicate **continuously**.

For example:

```text
User: "Book a meeting tomorrow."

AI: "Sure. What time?"

User: "10 AM."

AI: "Who should I invite?"

User: "John."

AI: "Meeting created."
```

The communication continuously goes:

```text
User ⇄ AI
```

This is where **WebSocket** becomes useful.

---

#### WebSocket Keeps the Connection Open




# 4. Building Typed APIs with Pydantic Models

## Goal

Make sure users send **correct and predictable input** before we pass anything into our AI system.

Expected:

```json
{
    "message": "What is RAG?",
    "temperature": 0.7
}
```

Invalid:

```json
{
    "message": "",
    "temperature": 999
}
```

We need validation.



## Mental Model

```text
User
 ↓
JSON
 ↓
Pydantic
 ↓
Valid?
 ├── NO → Reject
 │
 └── YES
       ↓
     AI Logic
```

### Takeaway

> **Never trust data coming from outside the application. Validate it first.**

---



# 5. Adding Authentication, Authorization, and API Keys

## Goal

Before understanding the code, let's understand the **problem we are trying to solve**.

Imagine we have built an AI platform called:

```text
MyAI
```

Our platform has three types of users:

```text
Free User
Premium User
Admin User
```

They have different permissions:

```text
Free User
→ Basic AI Chat

Premium User
→ Basic AI Chat
→ Premium AI Chat

Admin User
→ Basic AI Chat
→ Premium AI Chat
→ Admin Features
```

Whenever someone calls our API, our backend needs to answer two important questions:

```text
1. Who are you?

2. What are you allowed to do?
```

These two questions give us:

```text
Authentication
+
Authorization
```

---

# 5.1 Authentication

## What Is Authentication?

Authentication answers:

```text
Who are you?
```

Suppose somebody tries to access our AI API:

```text
POST /secure-chat
```

Our backend needs some way to identify or verify the caller.

One simple way is using an:

```text
API Key
```

For example:

```text
my-secret-key
```

The client sends this key with the request:

```text
X-API-Key: my-secret-key
```

Our server checks:

```text
Is this API key valid?
```

If the key is correct:

```text
Authentication Successful ✅
```

If the key is incorrect:

```text
Authentication Failed ❌

401 Unauthorized
```

So remember:

> **Authentication = Who are you?**

---

# What Is an API Key?

An API key is a secret value that a client sends when calling an API.

Think about an API key like a **hotel room key card**.

When you check into a hotel, you receive:

```text
Room Key Card
```

The card gives you access.

Similarly, an application may receive:

```text
API Key

abc123xyz
```

When calling the API:

```text
Client
   │
   │ X-API-Key: abc123xyz
   ↓
Server
```

The server checks the API key before allowing access.

So an API key can be used as a simple authentication mechanism for an API.

---



# Authentication Flow

```text
              API Request
                   ↓
            Send X-API-Key
                   ↓
           verify_api_key()
                   ↓
            Is Key Correct?
              /         \
            NO           YES
            ↓             ↓
       401 Error      AI Endpoint
                          ↓
                     AI Response
```

---



# 5.2 Authorization

Now let's understand **Authorization**.

Authentication answered:

```text
Who are you?
```

Authorization answers:

```text
What are you allowed to do?
```

Imagine our AI platform has three users.

```text
API KEY          ROLE

free-123         free

premium-456      premium

admin-789        admin
```

All three API keys are valid.

Therefore:

```text
free-123
→ Authenticated ✅

premium-456
→ Authenticated ✅

admin-789
→ Authenticated ✅
```

But they don't necessarily have the same permissions.

---

# Real-World Example

Our AI platform has:

```text
/basic-chat
```

Everyone can access it.

But we also have:

```text
/premium-chat
```

Only these users should access it:

```text
Premium User

Admin User
```

Now imagine the user sends:

```text
X-API-Key: free-123
```

The key exists.

Therefore:

```text
Authentication

Who are you?

→ Free User

PASSED ✅
```

But the user tries to access:

```text
/premium-chat
```

The Free User doesn't have permission.

Therefore:

```text
Authorization

Can you access Premium Chat?

FAILED ❌
```

The server returns:

```text
403 Forbidden
```

---



# Complete Authentication + Authorization Flow

```text
                    API Request
                        │
                        ↓
                  Send API Key
                        │
                        ↓
              ┌──────────────────┐
              │  AUTHENTICATION  │
              │                  │
              │   Who are you?   │
              └──────────────────┘
                        │
                  Valid API Key?
                    /       \
                  NO         YES
                  ↓           ↓
             401 Error    User Found
                              │
                              ↓
                    ┌──────────────────┐
                    │  AUTHORIZATION   │
                    │                  │
                    │ Can you do this? │
                    └──────────────────┘
                              │
                        Has Permission?
                          /       \
                        NO         YES
                        ↓           ↓
                   403 Error    AI Endpoint
                                    ↓
                               AI Response
```

---




# 6. Implementing Rate Limiting, Retries, Timeouts, and Circuit Breakers

## Goal

Make the AI API **resilient when users or external services behave unexpectedly.**

Memory trick:

```text
Rate Limit      → Protect from USERS

Retry           → Temporary FAILURE

Timeout         → Protect from WAITING

Circuit Breaker → Protect from FAILED SERVICES
```

---

# 6.1 Rate Limiting

## Problem

```text
One user
   ↓
10,000 requests
   ↓
LLM API
   ↓
Huge bill
```

## Goal

Restrict how many requests a user can make in a period.



Try:

```text
/limited?user_id=bappy
```

Expected:

```text
Request 1 ✅
Request 2 ✅
Request 3 ✅
Request 4 ✅
Request 5 ✅

Request 6 ❌
429 Too Many Requests
```

### Important Production Note

This dictionary is only for learning. In production, distributed systems normally use shared storage such as Redis or an API gateway.

---

# 6.2 Retry

## Problem

LLM providers sometimes fail temporarily.

## Goal

Try temporary failures again before giving up.

```text
Attempt 1 ❌
Wait

Attempt 2 ❌
Wait

Attempt 3 ✅
```



### Takeaway

> **Retries are useful for temporary failures. Do not blindly retry every possible error.**

---

# 6.3 Timeout

## Problem

What if an LLM or external API never responds?

## Goal

Put a maximum waiting time around external operations.



Because:

```text
LLM = 10 seconds

Timeout = 5 seconds
```

The endpoint should return:

```text
504
LLM request timed out
```

### Takeaway

> **Never allow an external operation to wait forever.**

---

# 6.4 Circuit Breaker

## Problem

Suppose the LLM provider is completely down.

```text
Request 1 → LLM ❌
Request 2 → LLM ❌
Request 3 → LLM ❌
Request 4 → LLM ❌
...
```

Why continue calling a service we already know is unhealthy?

## Goal

Temporarily stop requests after repeated failures.

```text
Failures reach threshold
        ↓
OPEN CIRCUIT
        ↓
Stop requests temporarily
        ↓
Wait
        ↓
Try provider again
```



### Mental Model

```text
CLOSED
 ↓
Requests allowed

3 failures
 ↓
OPEN
 ↓
Requests blocked

Wait

Try again
```

### Production Note

This implementation is for understanding the concept. Production applications normally use a tested resilience library or platform.

---



# 7. Making LLM Requests Idempotent

## Goal

Prevent the **same logical request from accidentally executing multiple times.**

Example:

```text
Generate Report
     ↓
LLM executes ✅
     ↓
Network response lost ❌
     ↓
Client retries
     ↓
LLM executes AGAIN ❌
```

For agents:

```text
Send Email ✅

Retry

Send Email AGAIN ❌
```

---



### Takeaway

> **Same idempotency key = same logical operation. Do not accidentally execute expensive or side-effecting work twice.**

---



# 8. Managing Secrets and Environment Configuration

## Goal

Keep passwords, API keys, database credentials, and environment-specific settings outside source code.

Bad:

```python
OPENAI_API_KEY = "sk-super-secret-key"
```

Then:

```bash
git add .
git commit
git push
```

The secret may become exposed.

---

## `.env`

```env
APP_NAME=Production AI API

ENVIRONMENT=development

LLM_API_KEY=my-secret-key

LLM_MODEL=demo-model
```

---

## `.gitignore`

```gitignore
# Never commit environment file
.env

# Python-generated folders
__pycache__/

# pytest-generated files
.pytest_cache/
```

---

## `config.py`



### Environment Mental Model

```text
              SAME CODE
                 │
       ┌─────────┼─────────┐
       ↓         ↓         ↓
      DEV       TEST      PROD
       │         │         │
   Dev Keys   Test Keys  Prod Keys
```

### Takeaway

> **Configuration changes between environments. Source code should not need to.**

---


# Note:
Building an LLM application is about making the AI work. Production AI engineering is about making the AI system continue to work when real users, real traffic, real failures, real costs, and real infrastructure enter the picture.