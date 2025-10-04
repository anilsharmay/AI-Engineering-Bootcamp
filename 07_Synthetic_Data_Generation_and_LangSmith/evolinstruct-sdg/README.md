# Evol-Instruct Synthetic Data Generation

## LangGraph-Based Question Evolution System

This folder contains the **LangGraph Evol-Instruct Synthetic Data Generation system** - an advanced alternative to the traditional RAGAS Knowledge Graph approach.

### 🎯 **Key Features:**
- **Evol-Instruct Methodology**: Progressive instruction evolution from simple to complex
- **Three Evolution Types**: Simple, Multi-Context, and Reasoning Evolution  
- **Agent-Based Architecture**: LangGraph agents orchestrate the entire process
- **Document-Driven**: Uses same documents from "data" folder as original SDG system

### 📁 **Files:**
- **`LangGraph_EVOL_Instruct_SDG.ipynb`** - Main notebook with complete implementation
- **`langgraph_accurate_workflow.png`** - Accurate workflow visualization with self-loops
- **`langgraph_workflow.png`** - Mermaid diagram of the workflow
- **`langgraph_evol_instruct_workflow.mmd`** - Mermaid source code
- **`langgraph_evol_instruct_results.json`** - Generated synthetic data results

### 🏗️ **Architecture:**
```
📥 Input Documents → 🔍 Document Analysis → ❓ Base Questions → 🌱 Evolution Loop → 📝 Answers → 📋 Contexts → 📤 Output
```

### 🎯 **Output Structure:**
- `List[dict]`: Evolved Questions with IDs and Evolution Types
- `List[dict]`: Question IDs with Answers  
- `List[dict]`: Question IDs with Relevant Contexts

### 🚀 **Usage:**
1. Open `LangGraph_EVOL_Instruct_SDG.ipynb`
2. Run all cells to execute the system
3. View results in pandas DataFrames
4. Analyze generated synthetic data

### 📊 **Benefits over RAGAS KG:**
- **More flexible**: Agents can adapt behavior based on content
- **Better evolution**: Progressive complexity through self-loops
- **Richer context**: Multi-document reasoning capabilities
- **Observable**: Full LangSmith tracing and logging
- **Scalable**: Easy to add new evolution types
