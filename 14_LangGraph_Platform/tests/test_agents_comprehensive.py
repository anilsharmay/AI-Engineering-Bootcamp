"""
Comprehensive test suite for both LangGraph agents.

This script demonstrates how to test both agents with various types of queries
to evaluate their capabilities and differences.
"""

from langgraph_sdk import get_sync_client
from .test_messages_examples import (
    get_test_messages_for_simple_agent,
    get_test_messages_for_helpfulness_agent,
    get_all_test_categories
)


def test_simple_agent():
    """Test the simple agent with various query types."""
    print("Testing Simple Agent")
    print("=" * 50)
    
    client = get_sync_client(url="http://localhost:2024")
    test_messages = get_test_messages_for_simple_agent()
    
    for category, messages in test_messages.items():
        print(f"\n--- Testing {category.upper()} queries ---")
        
        for i, message in enumerate(messages[:2]):  # Test first 2 from each category
            print(f"\nTest {i+1}: {message['content'][:60]}...")
            
            try:
                for chunk in client.runs.stream(
                    None,  # Threadless run
                    "simple_agent",  # Assistant id from langgraph.json
                    input={"messages": [message]},
                    stream_mode="updates",
                ):
                    if chunk.event == "messages/partial":
                        print(f"  Partial response: {chunk.data.get('content', '')[:100]}...")
                    elif chunk.event == "messages/complete":
                        print(f"  Complete response: {chunk.data.get('content', '')[:200]}...")
                    elif chunk.event == "messages/tool_calls":
                        print(f"  Tool calls: {len(chunk.data.get('tool_calls', []))} tools invoked")
                        
            except Exception as e:
                print(f"  Error: {e}")


def test_helpfulness_agent():
    """Test the agent with helpfulness check."""
    print("\n\nTesting Agent with Helpfulness Check")
    print("=" * 50)
    
    client = get_sync_client(url="http://localhost:2024")
    test_messages = get_test_messages_for_helpfulness_agent()
    
    for category, messages in test_messages.items():
        print(f"\n--- Testing {category.upper()} queries ---")
        
        for i, message in enumerate(messages[:2]):  # Test first 2 from each category
            print(f"\nTest {i+1}: {message['content'][:60]}...")
            
            try:
                for chunk in client.runs.stream(
                    None,  # Threadless run
                    "agent_helpful",  # Assistant id from langgraph.json
                    input={"messages": [message]},
                    stream_mode="updates",
                ):
                    if chunk.event == "messages/partial":
                        print(f"  Partial response: {chunk.data.get('content', '')[:100]}...")
                    elif chunk.event == "messages/complete":
                        print(f"  Complete response: {chunk.data.get('content', '')[:200]}...")
                    elif chunk.event == "messages/tool_calls":
                        print(f"  Tool calls: {len(chunk.data.get('tool_calls', []))} tools invoked")
                    elif chunk.event == "messages/partial" and "HELPFULNESS:" in str(chunk.data):
                        print(f"  Helpfulness check: {chunk.data}")
                        
            except Exception as e:
                print(f"  Error: {e}")


def test_specific_query(agent_id: str, query: str):
    """Test a specific query with a specific agent."""
    print(f"\nTesting {agent_id} with query: {query[:60]}...")
    
    client = get_sync_client(url="http://localhost:2024")
    
    try:
        for chunk in client.runs.stream(
            None,  # Threadless run
            agent_id,
            input={"messages": [{"role": "human", "content": query}]},
            stream_mode="updates",
        ):
            print(f"Event: {chunk.event}")
            if hasattr(chunk, 'data') and chunk.data:
                print(f"Data: {chunk.data}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")


def compare_agents_on_same_query(query: str):
    """Compare both agents on the same query to see differences."""
    print(f"\nComparing both agents on: {query}")
    print("=" * 60)
    
    # Test simple agent
    print("\n--- Simple Agent Response ---")
    test_specific_query("simple_agent", query)
    
    # Test helpfulness agent
    print("\n--- Agent with Helpfulness Response ---")
    test_specific_query("agent_helpful", query)


def main():
    """Main test function."""
    print("LangGraph Agent Testing Suite")
    print("=" * 50)
    
    # Show available test categories
    categories = get_all_test_categories()
    print("\nAvailable test categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category['category']}: {category['description']}")
    
    print("\nChoose test mode:")
    print("1. Test Simple Agent")
    print("2. Test Agent with Helpfulness")
    print("3. Compare both agents on specific query")
    print("4. Test specific query with specific agent")
    
    # For demonstration, let's run a few key tests
    print("\nRunning demonstration tests...")
    
    # Test a basic query with both agents
    compare_agents_on_same_query("What is the current population of Tokyo?")
    
    # Test an academic query
    compare_agents_on_same_query("What is the MuonClip optimizer, and what paper did it first appear in?")
    
    # Test a RAG query
    compare_agents_on_same_query("How are people using AI in their daily work?")


if __name__ == "__main__":
    main()
