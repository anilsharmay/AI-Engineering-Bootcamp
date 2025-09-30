# Research Graph Flow Analysis - Version 3 (Annotations)

This document shows a clean representation of the `research_graph` flow using annotations to show state interactions.

## Key Improvement

**Version 3** uses **annotations** directly on each node to show what state data they read and write, making the diagram cleaner and more focused.

## What Changed

### Before (V2 - Too Busy):
- Separate subgraph for shared state
- Multiple bidirectional arrows
- Cluttered appearance

### After (V3 - Clean Annotations):
- State interactions shown as annotations on each node
- Clean, focused flow
- Easy to understand at a glance

## State Annotations Explained

Each node shows:
- **📊 Reads**: What state data the node reads
- **📝 Writes**: What state data the node writes

### Node State Interactions:

- **ResearchSupervisor**: 
  - Reads: `messages`, `team_members` (for context and available agents)
  - Writes: `next` (decision), `messages` (conversation history)
  
- **Search Agent**: 
  - Reads: `messages` (for context)
  - Writes: `messages` (search results)
  
- **RAG Agent**: 
  - Reads: `messages` (for context)
  - Writes: `messages` (retrieval results)

## Benefits of V3 Representation

1. **Clean**: No cluttered state connections
2. **Focused**: Shows the actual execution flow clearly
3. **Informative**: State interactions are clearly visible
4. **Readable**: Easy to understand at a glance
5. **Accurate**: Shows exactly what each node does with state

## Files
- **Mermaid Source**: [`research_graph_flow_v2.mmd`](research_graph_flow_v2.mmd)
- **Generated Image**: [`research_graph_flow_v2.png`](research_graph_flow_v2.png)
