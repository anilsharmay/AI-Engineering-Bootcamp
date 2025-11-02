"""LangGraph Agent Library

A library for LangGraph agents with caching, monitoring, and agent integration.
"""

from .agents import create_langgraph_agent, create_helpfulness_agent
from .caching import CacheBackedEmbeddings, setup_llm_cache
from .rag import ProductionRAGChain
from .models import get_openai_model

# Optional guarded agents (only if guardrails available)
try:
    from .guarded_agents import (
        create_guarded_agent,
        create_guards_for_agent,
        GuardedAgentState
    )
    GUARDED_AGENTS_AVAILABLE = True
except ImportError:
    GUARDED_AGENTS_AVAILABLE = False

__version__ = "0.1.0"
__all__ = [
    "create_langgraph_agent",
    "create_helpfulness_agent",
    "CacheBackedEmbeddings",
    "setup_llm_cache",
    "ProductionRAGChain",
    "get_openai_model",
]

if GUARDED_AGENTS_AVAILABLE:
    __all__.extend([
        "create_guarded_agent",
        "create_guards_for_agent",
        "GuardedAgentState",
    ])

