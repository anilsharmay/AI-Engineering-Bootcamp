"""
Quick test messages for both LangGraph agents.

Simple examples you can copy-paste into your test_served_graph.py file.
"""

# =============================================================================
# QUICK TEST MESSAGES FOR SIMPLE AGENT
# =============================================================================

simple_agent_tests = [
    # Basic information queries
    {
        "role": "human",
        "content": "What is the current population of Tokyo?"
    },
    {
        "role": "human",
        "content": "What are the main ingredients in a traditional margherita pizza?"
    },
    
    # Academic research queries
    {
        "role": "human",
        "content": "What is the MuonClip optimizer, and what paper did it first appear in?"
    },
    {
        "role": "human",
        "content": "Find recent papers on transformer architecture improvements in 2024"
    },
    
    # RAG queries (local document search)
    {
        "role": "human",
        "content": "How are people using AI in their daily work?"
    },
    {
        "role": "human",
        "content": "What are the main trends in AI adoption in the workplace?"
    },
    
    # Complex multi-step queries
    {
        "role": "human",
        "content": "Compare the latest research on large language models with how people are actually using AI in practice. What gaps exist?"
    },
    
    # Edge cases
    {
        "role": "human",
        "content": "What's the weather like on Mars right now?"
    }
]

# =============================================================================
# QUICK TEST MESSAGES FOR AGENT WITH HELPFULNESS
# =============================================================================

helpfulness_agent_tests = [
    # All the same as simple agent, plus these helpfulness-specific tests:
    {
        "role": "human",
        "content": "I need a very detailed, comprehensive explanation of how neural networks work, including mathematical formulations, implementation details, and practical examples."
    },
    {
        "role": "human",
        "content": "Can you provide a complete analysis of the AI job market, including salary ranges, required skills, job growth projections, and specific companies hiring?"
    },
    {
        "role": "human",
        "content": "I want to understand the complete history of artificial intelligence from the 1950s to present, including all major milestones, key figures, and paradigm shifts."
    }
]

# =============================================================================
# EXAMPLE USAGE IN test_served_graph.py
# =============================================================================

def example_usage():
    """
    Example of how to use these messages in your test_served_graph.py:
    
    # For simple agent:
    input={
        "messages": simple_agent_tests[0]  # or any index
    }
    
    # For agent with helpfulness:
    input={
        "messages": helpfulness_agent_tests[0]  # or any index
    }
    """
    pass

# =============================================================================
# PRINT ALL TEST MESSAGES
# =============================================================================

if __name__ == "__main__":
    print("SIMPLE AGENT TEST MESSAGES:")
    print("=" * 40)
    for i, msg in enumerate(simple_agent_tests, 1):
        print(f"{i}. {msg['content']}")
    
    print("\n\nAGENT WITH HELPFULNESS TEST MESSAGES:")
    print("=" * 40)
    for i, msg in enumerate(helpfulness_agent_tests, 1):
        print(f"{i}. {msg['content']}")
    
    print("\n\nTO USE IN test_served_graph.py:")
    print("=" * 40)
    print("Replace the 'messages' array with any of the above messages.")
    print("Example:")
    print("input={")
    print('    "messages": [')
    print('        {')
    print('            "role": "human",')
    print('            "content": "What is the current population of Tokyo?"')
    print('        }')
    print('    ]')
    print('}')
