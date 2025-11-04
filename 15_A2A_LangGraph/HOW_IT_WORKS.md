# How It Works: A2A LangGraph Agent

This document explains how the A2A (Agent-to-Agent) protocol agent works, focusing on component relationships, workflows, and key concepts.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Relationships](#component-relationships)
3. [Client Discovery & Communication Flow](#client-discovery--communication-flow)
4. [Execution Flow](#execution-flow)
5. [Key Concepts](#key-concepts)

---

## Architecture Overview

The system implements an **Agent-to-Agent (A2A) protocol** agent with a **helpfulness evaluation loop**. It's built in 5 layers:

```
┌─────────────────────────────────────────────────────────┐
│ 1. Server Layer (__main__.py)                          │
│    - Exposes A2A protocol endpoints                     │
│    - Serves AgentCard for discovery                     │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ 2. Request Handling (agent_executor.py)                │
│    - Validates requests                                 │
│    - Manages task state                                 │
│    - Handles streaming                                  │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ 3. Agent Layer (agent.py)                              │
│    - Core agent with LangGraph                          │
│    - Streaming responses                                │
│    - Response formatting                                │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ 4. Graph Execution (agent_graph_with_helpfulness.py)   │
│    - Tool execution                                     │
│    - Helpfulness evaluation                             │
│    - Loop control                                       │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ 5. Tools Layer (tools.py, rag.py)                      │
│    - Tavily (web search)                                │
│    - ArXiv (academic papers)                            │
│    - RAG (document retrieval)                           │
└─────────────────────────────────────────────────────────┘
```

---

## Component Relationships

### How Server, AgentCard, and Agent Relate

#### **AgentCard** = "Business Card" (Metadata)
- **Purpose**: Describes what the agent can do
- **Location**: Created in `__main__.py` (lines 72-81)
- **Contains**:
  - Name, description, version
  - URL where agent lives
  - Capabilities (streaming, push notifications)
  - Skills (web_search, arxiv_search, rag_search)
  - Input/output formats (from `Agent.SUPPORTED_CONTENT_TYPES`)

**Think of it as**: A public API specification that other agents/clients read to discover capabilities.

#### **Agent** = "The Brain" (Logic)
- **Purpose**: The actual AI agent that processes queries
- **Location**: `agent.py`
- **Contains**:
  - LangGraph with helpfulness evaluation
  - Tool access (web search, ArXiv, RAG)
  - Streaming responses
  - Response formatting

#### **Server** = "The Front Door" (Infrastructure)
- **Purpose**: Exposes the agent via HTTP/A2A protocol
- **Location**: `__main__.py` (lines 95-99)
- **Components**:
  - `A2AStarletteApplication` - A2A protocol server
  - `DefaultRequestHandler` - Handles HTTP requests
  - `GeneralAgentExecutor` - Bridges requests to the Agent

### Connection Diagram

```
┌─────────────────────────────────────────────────┐
│  Server (A2AStarletteApplication)               │
│  - Exposes HTTP endpoints                       │
│  - Serves AgentCard at /.well-known/agent-card │
│  - Receives requests                            │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Uses AgentCard for discovery
                    │ Routes requests to:
                    ▼
┌─────────────────────────────────────────────────┐
│  RequestHandler (DefaultRequestHandler)         │
│  - Validates requests                           │
│  - Manages task state                           │
│  - Handles streaming                            │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Delegates execution to:
                    ▼
┌─────────────────────────────────────────────────┐
│  AgentExecutor (GeneralAgentExecutor)           │
│  - Creates Agent instance                       │
│  - Calls agent.stream()                         │
│  - Formats responses                            │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Executes:
                    ▼
┌─────────────────────────────────────────────────┐
│  Agent (Agent class)                            │
│  - Runs LangGraph                               │
│  - Uses tools                                   │
│  - Evaluates helpfulness                        │
│  - Returns structured responses                 │
└─────────────────────────────────────────────────┘
```

### Code Flow at Startup

```python
# In __main__.py:

# 1. Create AgentCard (metadata)
agent_card = AgentCard(
    name='General Purpose Agent',
    skills=[...],  # web_search, arxiv_search, rag_search
    capabilities=AgentCapabilities(...),
    default_input_modes=Agent.SUPPORTED_CONTENT_TYPES,  # Links to Agent
    ...
)

# 2. Create AgentExecutor (which wraps Agent)
request_handler = DefaultRequestHandler(
    agent_executor=GeneralAgentExecutor()  # ← Creates Agent internally
)

# 3. Create Server with both
server = A2AStarletteApplication(
    agent_card=agent_card,      # ← For discovery
    http_handler=request_handler # ← For execution
)
```

**Key Point**: The AgentCard uses `Agent.SUPPORTED_CONTENT_TYPES` (line 77-78) to declare what formats the Agent accepts, keeping metadata and implementation aligned.

---

## Client Discovery & Communication Flow

### Step 1: Discovery - Finding the Agent

The client uses the **well-known path** to fetch the AgentCard:

```python
# Client knows the base URL (e.g., http://localhost:10000)
resolver = A2ACardResolver(
    httpx_client=httpx_client,
    base_url='http://localhost:10000',
)

# Fetches AgentCard from well-known endpoint
public_card = await resolver.get_agent_card()
# This makes GET request to: http://localhost:10000/.well-known/agent-card
```

**What happens:**
- Client sends GET to `http://localhost:10000/.well-known/agent-card`
- Server returns AgentCard JSON with:
  - Name, description, capabilities
  - Skills (web_search, arxiv_search, rag_search)
  - Input/output formats
  - API endpoints

**Discovery Path**: `AGENT_CARD_WELL_KNOWN_PATH` = `/.well-known/agent-card`

### Step 2: Initialize Client - Setup for Communication

```python
# Client is initialized with the discovered AgentCard
client = A2AClient(
    httpx_client=httpx_client,
    agent_card=final_agent_card_to_use  # From Step 1
)
```

The AgentCard tells the client:
- How to format requests
- What endpoints to use
- What the agent can do

### Step 3: Create Task - Delegating Work

The client creates a task by sending a message:

```python
# Build the message payload
send_message_payload = {
    'message': {
        'role': 'user',
        'parts': [
            {'kind': 'text', 'text': 'Find recent papers on transformers'}
        ],
        'message_id': uuid4().hex,  # Unique message ID
    },
}

# Wrap in A2A protocol request
request = SendMessageRequest(
    id=str(uuid4()),  # Unique request ID
    params=MessageSendParams(**send_message_payload)
)

# Send to agent server
response = await client.send_message(request)
```

**What happens on the server:**
1. `A2AStarletteApplication` receives the HTTP request
2. `DefaultRequestHandler` processes it
3. `GeneralAgentExecutor.execute()` is called:
   ```python
   # In agent_executor.py
   query = context.get_user_input()  # Extracts "Find recent papers..."
   task = new_task(context.message)  # Creates new task
   await event_queue.enqueue_event(task)  # Task is created
   ```

**Response includes:**
- `task_id` - Unique task identifier
- `context_id` - Conversation context ID
- Task status

### Step 4: Agent Execution - Processing the Task

The server delegates to the Agent:

```python
# In GeneralAgentExecutor.execute()
async for item in self.agent.stream(query, task.context_id):
    # Agent processes the query
    # Uses tools (ArXiv search, etc.)
    # Evaluates helpfulness
    # Streams updates...
```

**Agent execution flow:**
1. `Agent.stream()` called with query + context_id
2. LangGraph processes:
   - Agent node decides to use ArXiv tool
   - Action node executes ArXiv search
   - Helpfulness node evaluates response
3. Real-time updates streamed:
   ```python
   yield {'content': 'Searching for information...'}  # During tool execution
   yield {'content': 'Processing results...'}        # After tools
   yield {'content': 'Final answer...', 'is_task_complete': True}  # Final
   ```

### Step 5: Receive Response - Getting Results

The client receives updates in real time:

**Option A: Non-streaming** (waits for completion)
```python
response = await client.send_message(request)
# Response contains:
# - task_id
# - context_id  
# - result (when complete)
# - task state (working, completed, input_required)
```

**Option B: Streaming** (real-time updates)
```python
stream_response = client.send_message_streaming(streaming_request)

async for chunk in stream_response:
    # Receives chunks as they're generated:
    # - Status updates: "Searching...", "Processing..."
    # - Progress updates
    # - Final result when complete
```

### Step 6: Multi-turn Conversation - Continuing the Dialogue

For follow-up questions, **only reuse `context_id`** (not `task_id`). The server creates a new `task_id` for each message:

```python
# First message (creates task)
response = await client.send_message(request)
task_id = response.root.result.id  # Store for reference, but don't reuse
context_id = response.root.result.context_id  # Reuse for follow-ups

# Follow-up message (continues conversation)
second_request = SendMessageRequest(
    id=str(uuid4()),
    params=MessageSendParams(**{
        'message': {
            'role': 'user',
            'parts': [{'kind': 'text', 'text': 'Summarize key findings?'}],
            'message_id': uuid4().hex,
            # Do NOT include task_id - server creates new task for each message
            'context_id': context_id,  # ← Only reuse context_id
        },
    })
)

second_response = await client.send_message(second_request)
# New response will have a new task_id, but same context_id
```

**What happens:**
- Server uses `context_id` to retrieve conversation history
- Server creates a **new `task_id`** for each message (tasks are single-turn)
- Agent's memory (`MemorySaver`) maintains context per `context_id`
- Agent can reference previous messages in the conversation

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  CLIENT AGENT                                           │
└─────────────────────────────────────────────────────────┘
                    │
    Step 1: Discovery
                    │
                    ▼
    GET http://localhost:10000/.well-known/agent-card
                    │
                    ▼
    Receives AgentCard (capabilities, skills, endpoints)
                    │
    Step 2: Initialize
                    │
                    ▼
    A2AClient(agent_card=discovered_card)
                    │
    Step 3: Create Task & Delegate
                    │
                    ▼
    POST /send_message
    {message: "Find papers on transformers"}
                    │
                    ├─────────────────────────────────────┐
                    │                                     │
┌───────────────────▼─────────────────────────────────────▼──────┐
│  SERVER AGENT                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ A2AStarletteApplication                                  │ │
│  │ - Serves AgentCard at /.well-known/agent-card           │ │
│  │ - Receives /send_message requests                       │ │
│  └───────────────┬─────────────────────────────────────────┘ │
│                  │                                            │
│                  ▼                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ DefaultRequestHandler                                   │ │
│  │ - Creates task (task_id, context_id)                    │ │
│  │ - Manages task state                                    │ │
│  └───────────────┬─────────────────────────────────────────┘ │
│                  │                                            │
│                  ▼                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ GeneralAgentExecutor                                    │ │
│  │ - Calls agent.stream(query, context_id)                 │ │
│  │ - Streams updates to EventQueue                         │ │
│  └───────────────┬─────────────────────────────────────────┘ │
│                  │                                            │
│                  ▼                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Agent (LangGraph)                                       │ │
│  │ - Processes query                                       │ │
│  │ - Uses tools (ArXiv, Tavily, RAG)                      │ │
│  │ - Evaluates helpfulness                                 │ │
│  │ - Returns structured response                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                    │
                    │ Streams updates via EventQueue
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  CLIENT AGENT                                           │
│  Step 4-5: Receive Response                            │
│                                                         │
│  Receives:                                             │
│  - Status updates ("Searching...", "Processing...")    │
│  - Final result with answer                            │
│  - task_id & context_id for follow-ups                │
└─────────────────────────────────────────────────────────┘
```

---

## Execution Flow

### LangGraph Execution Loop

```
User Query → Agent Node
                 ↓
      [Has tool calls?]
      /              \
     YES              NO
     ↓                ↓
Action Node    Helpfulness Node
(run tools)    (evaluate response)
     ↓                ↓
Back to Agent    [Helpful?]
                     /    \
                   YES    NO (loop back, max 10x)
                    ↓
                  END
```

### Graph Nodes

1. **`agent` node** (`_call_model`):
   - Invokes LLM with conversation history
   - Binds tools (Tavily, ArXiv, RAG)
   - If no tool calls: extracts `ResponseFormat` via structured output
   - Returns response message and structured response

2. **`action` node** (`tool_node`):
   - Executes tool calls (Tavily search, ArXiv search, RAG retrieval)
   - Returns tool results as `ToolMessage`
   - Routes back to `agent` to process results

3. **`helpfulness` node** (`_helpfulness_node`):
   - Evaluates response quality
   - Compares initial query vs. final response
   - Returns `HELPFULNESS:Y` (helpful) or `HELPFULNESS:N` (not helpful)
   - Safety: stops after 10 iterations

### Routing Logic

- `route_to_action_or_helpfulness()`: Checks if last message has tool calls → route to `action`, else `helpfulness`
- `helpfulness_decision()`: Checks helpfulness marker → `END` if Y or END, else loop back to `agent`

### Example Execution

**User Query**: *"Find recent papers on transformers"*

1. **agent node**: LLM sees query, decides: "Need ArXiv search tool"
2. **route_to_action_or_helpfulness()**: Detects tool_calls → routes to "action"
3. **action node**: Executes ArxivQueryRun("transformers"), returns paper results
4. **Routes back to agent**
5. **agent node** (again): LLM processes tool results, generates response, extracts ResponseFormat
6. **route_to_action_or_helpfulness()**: No tool_calls → routes to "helpfulness"
7. **helpfulness node**: Compares query vs response, evaluates: "Does response answer the question well?", returns HELPFULNESS:Y
8. **helpfulness_decision()**: Sees "HELPFULNESS:Y" → routes to END

---

## Key Concepts

### A2A Protocol

The **Agent-to-Agent Protocol** enables standardized communication between AI agents:

- **Discovery**: Agents find each other via well-known endpoints
- **Standardization**: Common request/response format
- **Interoperability**: Agents from different frameworks can communicate
- **Self-description**: AgentCard provides metadata about capabilities

### Helpfulness Evaluation Loop

The agent has a built-in quality control mechanism:

1. After generating a response, a secondary LLM evaluates it
2. Checks if the response is "extremely helpful" (Y) or not (N)
3. If not helpful (N), loops back to improve the response
4. Maximum 10 iterations to prevent infinite loops

### Task & Context Management

- **Task**: A single request/response cycle, identified by `task_id`
  - Each message creates a **new task** with a new `task_id`
  - Tasks are completed after the first response
- **Context**: Conversation history, identified by `context_id`
  - `context_id` persists across multiple messages in the same conversation
  - Reuse `context_id` (but not `task_id`) for follow-up messages
- **Multi-turn**: Reuse `context_id` to maintain conversation state
  - Only `context_id` is reused for follow-ups (server creates new `task_id` for each message)
- **Memory**: `MemorySaver` checkpointer stores conversation history per `context_id`

### Tools Available

1. **Tavily Search**: Real-time web search
2. **ArXiv Search**: Academic paper search
3. **RAG Retrieval**: Document search from local PDFs (vector store)

### Response States

The agent returns structured responses with status:

- `completed`: Request successfully fulfilled
- `input_required`: User needs to provide more information
- `error`: Error occurred during processing

### Streaming

The agent supports real-time streaming:

- **During execution**: Status updates ("Searching...", "Processing...")
- **Tool execution**: Notifies when tools are being used
- **Final response**: Complete answer when done

---

## Summary

**The Big Picture:**

1. **Discovery**: Client fetches AgentCard from `/.well-known/agent-card`
2. **Initialize**: Client creates `A2AClient` with the AgentCard
3. **Create Task**: Client sends `SendMessageRequest` → Server creates task with new `task_id`
4. **Delegate**: Server routes to `Agent.stream()` → LangGraph processes
5. **Receive**: Client gets streaming updates → Final result with `task_id` and `context_id`
6. **Continue**: Client reuses `context_id` (only) for follow-ups - server creates new `task_id` for each message

This is the A2A protocol in action: agents discover each other, delegate work, and communicate through standardized endpoints, with built-in quality evaluation through the helpfulness loop.

