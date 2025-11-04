# Client-Server Interaction Diagram

This document contains Mermaid diagrams visualizing the interactions between the client agent and server agent using the A2A protocol.

## Server Agent LangGraph Flow (Reference)

```mermaid
graph TD
    START([User Query]) --> AGENT[agent node<br/>LLM + Tools]
    AGENT --> ROUTE{Has tool calls?}
    ROUTE -->|Yes| ACTION[action node<br/>Execute tools]
    ROUTE -->|No| HELPFUL[helpfulness node<br/>Evaluate response]
    ACTION --> AGENT
    HELPFUL --> DECISION{Helpful?}
    DECISION -->|Yes Y| END([END])
    DECISION -->|No N| LOOP{< 10 iterations?}
    LOOP -->|Yes| AGENT
    LOOP -->|No| END

    style START fill:#1e3a5f,stroke:#ffffff,stroke-width:3px,color:#ffffff
    style AGENT fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style ACTION fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style HELPFUL fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style END fill:#c62828,stroke:#ffffff,stroke-width:3px,color:#ffffff
```

## A2A Protocol Discovery Flow

```mermaid
graph LR
    CLIENT[Client Agent] -->|1. GET| SERVER["Server<br/>/.well-known/agent-card"]
    SERVER -->|2. AgentCard JSON| CLIENT
    CLIENT -->|3. Initialize| A2ACLIENT["Client-Side<br/>A2AClient Object"]
    A2ACLIENT -->|4. Ready to send| MESSAGES[messages]

    style CLIENT fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style SERVER fill:#2e7d32,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style A2ACLIENT fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style MESSAGES fill:#283593,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Multi-Turn Conversation Flow

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Memory

    Note over Client,Memory: Turn 1: Initial Query

    Client->>Server: SendMessageRequest<br/>{query: "Research multimodal AI"}
    Server->>Memory: Create new context_id
    Server->>Server: Process query (tools, helpfulness)
    Server->>Memory: Store conversation
    Server-->>Client: Response + task_id + context_id: "abc123"
    Note over Client: Store context_id: "abc123"

    Note over Client,Memory: Turn 2: Follow-up (Reuses Context)

    Client->>Server: SendMessageRequest<br/>{query: "Find papers",<br/>context_id: "abc123"}
    Server->>Memory: Load context_id: "abc123"
    Server->>Server: Process with conversation history
    Server->>Memory: Update conversation
    Server-->>Client: Response (with context)
    Note over Client: Server remembers previous conversation
```

## Tool Execution Flow (Server Side)

```mermaid
graph TD
    QUERY[User Query] --> AGENT[Agent Node<br/>LLM analyzes query]
    AGENT --> DECIDE{Which tool?}
    DECIDE -->|Web search| TAVILY[Tavily Search<br/>Real-time web results]
    DECIDE -->|Papers| ARXIV[ArXiv Search<br/>Academic papers]
    DECIDE -->|Documents| RAG[RAG Retrieval<br/>Local PDFs]
    TAVILY --> AGENT
    ARXIV --> AGENT
    RAG --> AGENT
    AGENT --> HELPFUL[Helpfulness Evaluation]
    HELPFUL --> RESPONSE[Response to Client]

    style QUERY fill:#1e3a5f,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style AGENT fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style TAVILY fill:#00695c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style ARXIV fill:#4527a0,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style RAG fill:#283593,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style HELPFUL fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style RESPONSE fill:#2e7d32,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Key Components Interaction

```mermaid
graph TB
    subgraph "Client Agent"
        CLIENT_GRAPH[LangGraph<br/>Client Agent]
        CLIENT_STATE[ClientAgentState]
        A2A_CLIENT[A2AClient]
    end

    subgraph "A2A Protocol"
        AGENT_CARD[AgentCard<br/>Discovery]
        PROTOCOL[A2A Protocol<br/>HTTP/JSON]
    end

    subgraph "Server Agent"
        SERVER_GRAPH[LangGraph<br/>Server Agent]
        SERVER_STATE[AgentState]
        TOOLS[Tools<br/>Tavily, ArXiv, RAG]
        MEMORY[MemorySaver<br/>Context Management]
    end

    CLIENT_GRAPH --> CLIENT_STATE
    CLIENT_GRAPH --> A2A_CLIENT
    A2A_CLIENT --> AGENT_CARD
    A2A_CLIENT --> PROTOCOL
    PROTOCOL --> SERVER_GRAPH
    SERVER_GRAPH --> SERVER_STATE
    SERVER_GRAPH --> TOOLS
    SERVER_GRAPH --> MEMORY

    style CLIENT_GRAPH fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style SERVER_GRAPH fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style PROTOCOL fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Current Client Agent Implementation (Simplified)

### Client Agent Graph Flow

```mermaid
graph TD
    START([START]) --> SEND_QUERY[send_query_node<br/>Send query to server<br/>Extract response]
    SEND_QUERY --> ASK_USER[ask_user_node<br/>Display response<br/>Ask user for refinement]
    ASK_USER --> DECISION{should_continue}
    DECISION -->|user_wants_refinement = True| SEND_QUERY
    DECISION -->|user_wants_refinement = False| DISPLAY[display_response_node<br/>Show all responses<br/>Summary table]
    DISPLAY --> END([END])

    style START fill:#1e3a5f,stroke:#ffffff,stroke-width:3px,color:#ffffff
    style SEND_QUERY fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style ASK_USER fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style DECISION fill:#f57c00,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style DISPLAY fill:#283593,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style END fill:#c62828,stroke:#ffffff,stroke-width:3px,color:#ffffff
```

### Client Agent State Structure

```mermaid
classDiagram
    class ClientAgentState {
        +str query
        +str base_url
        +AgentCard agent_card
        +A2AClient client
        +httpx.AsyncClient httpx_client
        +str task_id
        +str context_id
        +str response
        +list[str] all_responses
        +bool user_wants_refinement
        +list messages
    }

    class AgentCard {
        +str name
        +str description
        +str url
        +list skills
        +dict capabilities
    }

    class A2AClient {
        +send_message()
    }

    ClientAgentState --> AgentCard
    ClientAgentState --> A2AClient
```

### Main Function Flow

```mermaid
graph TD
    MAIN[main function] --> DISCOVER[Discover Agent<br/>discover_agent helper]
    DISCOVER --> BUILD[Build Graph<br/>build_client_agent_graph]
    BUILD --> LOOP[Interactive Loop]
    LOOP --> INPUT[User Input Query]
    INPUT --> CHECK{quit?}
    CHECK -->|Yes| CLEANUP[Close httpx_client]
    CHECK -->|No| INVOKE[Invoke Graph<br/>with initial state]
    INVOKE --> COMPLETE[Research Complete]
    COMPLETE --> LOOP
    CLEANUP --> EXIT([Exit])

    style MAIN fill:#1e3a5f,stroke:#ffffff,stroke-width:3px,color:#ffffff
    style DISCOVER fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style BUILD fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style LOOP fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style INVOKE fill:#2e7d32,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style EXIT fill:#c62828,stroke:#ffffff,stroke-width:3px,color:#ffffff
```

### Response Extraction Flow

```mermaid
graph TD
    RESPONSE[A2A Response Object] --> DUMP[model_dump to dict]
    DUMP --> CHECK_ERROR{Has error?}
    CHECK_ERROR -->|Yes| ERROR[Return Error]
    CHECK_ERROR -->|No| GET_RESULT[Get result from response]
    GET_RESULT --> EXTRACT[Extract task_id, contextId]
    GET_RESULT --> CHECK_ARTIFACTS{Has artifacts?}
    CHECK_ARTIFACTS -->|Yes| ARTIFACT[Extract from artifact.parts]
    CHECK_ARTIFACTS -->|No| CHECK_MESSAGES{Has messages?}
    CHECK_MESSAGES -->|Yes| MESSAGES[Extract from messages]
    CHECK_MESSAGES -->|No| CHECK_CONTENT{Has content?}
    CHECK_CONTENT -->|Yes| CONTENT[Use content field]
    CHECK_CONTENT -->|No| FALLBACK[JSON dump result]
    ARTIFACT --> RETURN[Return task_id, context_id, text]
    MESSAGES --> RETURN
    CONTENT --> RETURN
    FALLBACK --> RETURN

    style RESPONSE fill:#1e3a5f,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style ARTIFACT fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style MESSAGES fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style RETURN fill:#2e7d32,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

### User-Driven Refinement Loop

```mermaid
sequenceDiagram
    participant User
    participant Graph as LangGraph
    participant QueryNode as send_query_node
    participant AskNode as ask_user_node
    participant DisplayNode as display_response_node
    participant Server as A2A Server

    User->>Graph: Enter research topic
    Graph->>QueryNode: Execute send_query_node
    QueryNode->>Server: Send query via A2A
    Server-->>QueryNode: Response with task_id, context_id
    QueryNode->>QueryNode: Extract response text
    QueryNode->>Graph: Update state (response, task_id, context_id)
    
    Graph->>AskNode: Execute ask_user_node
    AskNode->>User: Display response
    AskNode->>User: Ask: "Want to refine?"
    User->>AskNode: "yes" or "no"
    
    alt User wants refinement
        AskNode->>User: "Enter follow-up question"
        User->>AskNode: New query
        AskNode->>Graph: Update state (query, user_wants_refinement=True)
        Graph->>QueryNode: Loop back (with context_id)
        QueryNode->>Server: Send follow-up (reuse context_id)
        Server-->>QueryNode: Response (with context)
        Note over QueryNode,Server: Server remembers conversation
    else User satisfied
        AskNode->>Graph: Update state (user_wants_refinement=False)
        Graph->>DisplayNode: Execute display_response_node
        DisplayNode->>User: Show all responses + summary
    end
```

### Component Architecture

```mermaid
graph TB
    subgraph "Main Function"
        MAIN[main]
        DISCOVER_FUNC[discover_agent helper]
        LOOP[Interactive Loop]
    end

    subgraph "LangGraph"
        GRAPH[build_client_agent_graph]
        STATE[ClientAgentState]
        SEND[send_query_node]
        ASK[ask_user_node]
        DISPLAY[display_response_node]
        DECISION[should_continue]
    end

    subgraph "Utilities"
        EXTRACT[extract_response_text]
    end

    subgraph "External"
        A2ACLIENT[A2AClient]
        SERVER[A2A Server]
    end

    MAIN --> DISCOVER_FUNC
    MAIN --> GRAPH
    MAIN --> LOOP
    DISCOVER_FUNC --> A2ACLIENT
    GRAPH --> STATE
    GRAPH --> SEND
    GRAPH --> ASK
    GRAPH --> DISPLAY
    GRAPH --> DECISION
    SEND --> EXTRACT
    SEND --> A2ACLIENT
    A2ACLIENT --> SERVER
    EXTRACT --> SEND

    style MAIN fill:#1e3a5f,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style GRAPH fill:#4a148c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style EXTRACT fill:#1b5e20,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style A2ACLIENT fill:#e65100,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

---

## Notes

- **Discovery**: Happens once at the start, then reused for all queries
- **Context Reuse**: `context_id` is reused to maintain conversation history
- **State Management**: Each node updates the state, which flows through the graph
- **Tool Execution**: Server agent decides which tools to use based on the query
- **Memory**: Server maintains conversation history per `context_id` using `MemorySaver`

