# Authoring Graph Flow Analysis

This document contains the detailed flow analysis of the `authoring_graph` LangGraph implementation.

## Flow Diagram

The authoring graph follows a hierarchical supervisor-agent pattern where a supervisor orchestrates the workflow between specialized writing and editing agents.

## Key Components

### 🎯 Entry Point
- **AuthoringSupervisor**: The central orchestrator that decides which agent to call next

### ✍️ Authoring Agents
- **DocWriter**: Creates and writes content using file tools
- **NoteTaker**: Creates outlines and references previous responses
- **CopyEditor**: Handles grammar, spelling, and style improvements

### 🛠️ Tools
- **File Tools**: Document creation, editing, and reading capabilities
- **Research Tools**: Outline creation and reference lookup
- **Edit Tools**: Content editing and refinement

### 📊 State Management
- **DocWritingState**: Shared state containing:
  - `messages`: List of BaseMessage (conversation history)
  - `team_members`: str (available agents)
  - `next`: str (next action to take)
  - `current_files`: str (files in working directory)

## Flow Characteristics

1. **Entry Point**: `AuthoringSupervisor` starts the flow
2. **Decision Making**: Supervisor decides which agent to call next based on the writing task
3. **Agent Execution**: 
   - `DocWriter` creates and writes content
   - `NoteTaker` creates outlines and researches
   - `CopyEditor` refines grammar and style
4. **Return Path**: All agents return to supervisor after completion
5. **State Management**: All nodes share the `DocWritingState`
6. **Termination**: Supervisor can decide to `FINISH` when writing is complete

## Execution Pattern

```
AuthoringSupervisor → [DocWriter|NoteTaker|CopyEditor] → AuthoringSupervisor → [DocWriter|NoteTaker|CopyEditor|FINISH]
```

The supervisor can iteratively call agents as needed, allowing for complex writing workflows that combine content creation, research, and editing.

## Source Files
- **Mermaid Source**: [`authoring_graph_flow.mmd`](authoring_graph_flow.mmd)
- **Generated Image**: [`authoring_graph_flow.png`](authoring_graph_flow.png)
