# LangGraph Agent Tests

This directory contains comprehensive test utilities for both LangGraph agents.

## Files

- **`test_served_graph.py`** - Original test file for basic agent testing
- **`test_agents_comprehensive.py`** - Full test suite comparing both agents
- **`test_messages_examples.py`** - Categorized test messages and utilities
- **`quick_test_messages.py`** - Simple copy-paste examples for quick testing

## Usage

### Quick Testing
```python
# Use quick_test_messages.py for simple copy-paste examples
python quick_test_messages.py
```

### Comprehensive Testing
```python
# Run the full test suite
python test_agents_comprehensive.py
```

### Basic Testing
```python
# Use the original test file
python test_served_graph.py
```

## Test Categories

1. **Basic Information** - Simple factual questions
2. **Academic Research** - ArXiv paper queries
3. **RAG Queries** - Local document retrieval
4. **Complex Multi-Step** - Multi-tool reasoning
5. **Edge Cases** - Challenging scenarios
6. **Helpfulness Testing** - For helpfulness evaluation agent

## Agent Comparison

The test suite allows you to compare:
- **Simple Agent** - Basic tool-calling agent
- **Agent with Helpfulness** - Includes helpfulness evaluation loop

Both agents have access to:
- Tavily Search (web search)
- ArXiv Query (academic papers)
- RAG tool (local document retrieval)
