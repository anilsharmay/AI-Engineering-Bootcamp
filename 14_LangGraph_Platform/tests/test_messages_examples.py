"""
Test message examples for both LangGraph agents.

This file contains categorized test messages to evaluate:
1. Simple Agent (basic tool-calling)
2. Agent with Helpfulness (includes helpfulness evaluation loop)

Each category tests different capabilities and complexity levels.
"""

# =============================================================================
# BASIC INFORMATION QUERIES
# =============================================================================

basic_queries = [
    {
        "category": "Basic Information",
        "description": "Simple factual questions that may require web search",
        "messages": [
            {
                "role": "human",
                "content": "What is the current population of Tokyo?"
            },
            {
                "role": "human", 
                "content": "What are the main ingredients in a traditional margherita pizza?"
            },
            {
                "role": "human",
                "content": "What is the capital of New Zealand?"
            },
            {
                "role": "human",
                "content": "How many days are in February during a leap year?"
            }
        ]
    }
]

# =============================================================================
# ACADEMIC RESEARCH QUERIES
# =============================================================================

academic_queries = [
    {
        "category": "Academic Research",
        "description": "Questions requiring ArXiv search for academic papers",
        "messages": [
            {
                "role": "human",
                "content": "What is the MuonClip optimizer, and what paper did it first appear in?"
            },
            {
                "role": "human",
                "content": "Find recent papers on transformer architecture improvements in 2024"
            },
            {
                "role": "human",
                "content": "What are the latest developments in few-shot learning? Show me the most recent papers."
            },
            {
                "role": "human",
                "content": "Search for papers on quantum machine learning published in the last 6 months"
            },
            {
                "role": "human",
                "content": "What is the current state of research on neural architecture search?"
            }
        ]
    }
]

# =============================================================================
# RAG-SPECIFIC QUERIES
# =============================================================================

rag_queries = [
    {
        "category": "RAG Queries",
        "description": "Questions that should trigger the RAG tool for local document retrieval",
        "messages": [
            {
                "role": "human",
                "content": "How are people using AI in their daily work?"
            },
            {
                "role": "human",
                "content": "What are the main trends in AI adoption in the workplace?"
            },
            {
                "role": "human",
                "content": "Tell me about AI projects and their domains"
            },
            {
                "role": "human",
                "content": "What insights can you provide about how people use AI tools?"
            }
        ]
    }
]

# =============================================================================
# COMPLEX MULTI-STEP QUERIES
# =============================================================================

complex_queries = [
    {
        "category": "Complex Multi-Step",
        "description": "Queries that may require multiple tools or reasoning steps",
        "messages": [
            {
                "role": "human",
                "content": "Compare the latest research on large language models with how people are actually using AI in practice. What gaps exist?"
            },
            {
                "role": "human",
                "content": "Find recent papers on AI ethics, then search for current news about AI regulation, and finally tell me how this relates to workplace AI usage patterns."
            },
            {
                "role": "human",
                "content": "What are the most cited papers on machine learning optimization in 2024, and how do they compare to traditional optimization methods?"
            },
            {
                "role": "human",
                "content": "Research the latest developments in computer vision, then find information about how people are using AI for image processing in their work."
            }
        ]
    }
]

# =============================================================================
# EDGE CASES AND CHALLENGING QUERIES
# =============================================================================

edge_case_queries = [
    {
        "category": "Edge Cases",
        "description": "Challenging queries that test agent robustness",
        "messages": [
            {
                "role": "human",
                "content": "I don't know what I want to know. Can you help me figure out what to ask?"
            },
            {
                "role": "human",
                "content": "What is the meaning of life, the universe, and everything?"
            },
            {
                "role": "human",
                "content": "Tell me something interesting that happened yesterday that I should know about."
            },
            {
                "role": "human",
                "content": "What's the weather like on Mars right now?"
            },
            {
                "role": "human",
                "content": "Can you help me debug this Python code: print('Hello World'"
            }
        ]
    }
]

# =============================================================================
# CONVERSATIONAL FLOW QUERIES
# =============================================================================

conversational_queries = [
    {
        "category": "Conversational Flow",
        "description": "Multi-turn conversations to test context retention",
        "messages": [
            {
                "role": "human",
                "content": "I'm interested in learning about machine learning. Where should I start?"
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help you get started with machine learning! There are several great entry points depending on your background and goals."
            },
            {
                "role": "human",
                "content": "I have a computer science background but I'm new to ML. What are the most important papers I should read?"
            },
            {
                "role": "human",
                "content": "Actually, let me be more specific - I'm particularly interested in deep learning for computer vision. What recent breakthroughs should I know about?"
            }
        ]
    }
]

# =============================================================================
# HELPFULNESS TESTING QUERIES
# =============================================================================

helpfulness_queries = [
    {
        "category": "Helpfulness Testing",
        "description": "Queries designed to test the helpfulness evaluation in agent_with_helpfulness",
        "messages": [
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
    }
]

# =============================================================================
# AGENT-SPECIFIC TEST FUNCTIONS
# =============================================================================

def get_test_messages_for_simple_agent():
    """Get test messages specifically for the simple agent."""
    return {
        "basic": basic_queries[0]["messages"],
        "academic": academic_queries[0]["messages"],
        "rag": rag_queries[0]["messages"],
        "complex": complex_queries[0]["messages"],
        "edge_cases": edge_case_queries[0]["messages"]
    }

def get_test_messages_for_helpfulness_agent():
    """Get test messages specifically for the agent with helpfulness check."""
    return {
        "basic": basic_queries[0]["messages"],
        "academic": academic_queries[0]["messages"],
        "rag": rag_queries[0]["messages"],
        "complex": complex_queries[0]["messages"],
        "edge_cases": edge_case_queries[0]["messages"],
        "helpfulness": helpfulness_queries[0]["messages"],
        "conversational": conversational_queries[0]["messages"]
    }

def get_all_test_categories():
    """Get all test categories with descriptions."""
    return [
        basic_queries[0],
        academic_queries[0],
        rag_queries[0],
        complex_queries[0],
        edge_case_queries[0],
        conversational_queries[0],
        helpfulness_queries[0]
    ]

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Test Messages for LangGraph Agents")
    print("=" * 50)
    
    print("\nSimple Agent Test Messages:")
    simple_tests = get_test_messages_for_simple_agent()
    for category, messages in simple_tests.items():
        print(f"\n{category.upper()}:")
        for i, msg in enumerate(messages[:2]):  # Show first 2 examples
            print(f"  {i+1}. {msg['content']}")
    
    print("\n" + "=" * 50)
    print("\nAgent with Helpfulness Test Messages:")
    helpful_tests = get_test_messages_for_helpfulness_agent()
    for category, messages in helpful_tests.items():
        print(f"\n{category.upper()}:")
        for i, msg in enumerate(messages[:2]):  # Show first 2 examples
            print(f"  {i+1}. {msg['content']}")
