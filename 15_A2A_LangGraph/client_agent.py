"""Simple Client Agent using A2A Protocol.

This LangGraph agent discovers and communicates with the A2A protocol server agent.
Built for Activity #1 - Research Assistant Agent.
"""

import asyncio
import json
import logging
from typing import Any, Dict, TypedDict, Annotated
from uuid import uuid4

import httpx
from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

console = Console()


class ClientAgentState(TypedDict):
    """State schema for the client agent graph."""
    query: str
    base_url: str
    agent_card: AgentCard | None
    client: A2AClient | None
    httpx_client: httpx.AsyncClient | None
    task_id: str | None
    context_id: str | None
    response: str | None
    all_responses: list[str]  # Accumulate all responses
    user_wants_refinement: bool | None
    messages: Annotated[list, lambda x, y: x + [y]]  # Message history


def extract_response_text(response) -> tuple[str | None, str | None, str]:
    """Extract task_id, context_id, and text content from A2A response.
    
    Args:
        response: A2A response object from client.send_message()
        
    Returns:
        tuple: (task_id, context_id, result_text)
    """
    task_id = None
    context_id = None
    result_text = ""
    
    try:
        # Convert response to dict for easier navigation
        response_dict = response.model_dump(mode='json', exclude_none=True)
        
        # Check for errors (JSON-RPC format has error at top level)
        if 'error' in response_dict:
            error_msg = response_dict['error']
            return None, None, f"Error: {error_msg}"
        
        # Navigate to result (JSON-RPC format has result at top level)
        result = None
        if 'result' in response_dict:
            result = response_dict['result']
        elif 'root' in response_dict and 'result' in response_dict['root']:
            result = response_dict['root']['result']
        
        if result and isinstance(result, dict):
            task_id = result.get('id')
            # contextId is camelCase in the response (fallback to snake_case)
            context_id = result.get('contextId') or result.get('context_id')
            
            # Try multiple ways to extract text
            # Method 1: Check for artifacts (structure: Part(root=TextPart(text=...)))
            artifacts = result.get('artifacts', [])
            
            if artifacts:
                artifact = artifacts[0]
                
                # Check for root.text (TextPart structure)
                if isinstance(artifact, dict):
                    root = artifact.get('root', {})
                    if isinstance(root, dict):
                        # TextPart has 'text' property directly
                        if 'text' in root:
                            result_text = root['text']
                        # Or check for parts within root
                        elif 'parts' in root:
                            parts = root['parts']
                            text_parts = []
                            for part in parts:
                                if isinstance(part, dict):
                                    if part.get('kind') == 'text':
                                        text_parts.append(part.get('text', ''))
                                    elif 'root' in part and isinstance(part['root'], dict):
                                        if 'text' in part['root']:
                                            text_parts.append(part['root']['text'])
                            result_text = '\n'.join(text_parts)
                    # Also check for parts directly in artifact
                    if not result_text:
                        parts = artifact.get('parts', [])
                        if parts:
                            text_parts = []
                            for part in parts:
                                if isinstance(part, dict):
                                    if part.get('kind') == 'text':
                                        text_parts.append(part.get('text', ''))
                                    elif 'root' in part:
                                        root = part['root']
                                        if isinstance(root, dict) and 'text' in root:
                                            text_parts.append(root['text'])
                            if text_parts:
                                result_text = '\n'.join(text_parts)
            
            # Method 2: Check for messages
            if not result_text and result.get('messages'):
                messages = result['messages']
                if messages:
                    last_msg = messages[-1]
                    if isinstance(last_msg, dict):
                        result_text = last_msg.get('content') or last_msg.get('text') or str(last_msg)
                    else:
                        result_text = str(last_msg)
            
            # Method 3: Check for direct content field
            if not result_text and result.get('content'):
                result_text = result.get('content')
            
            # Method 4: Dump the whole result as fallback
            if not result_text:
                result_text = json.dumps(result, indent=2)
                    
    except Exception as e:
        logger.exception("Error extracting response")
        console.print(f"[red]❌ Error extracting response: {e}[/red]")
        result_text = f"Response received but could not be parsed: {e}"
    
    return task_id, context_id, result_text


async def send_query_node(state: ClientAgentState) -> Dict[str, Any]:
    """Send query to the discovered agent."""
    console.print(Panel.fit(
        "[bold green]Step 1: Sending Query to Agent[/bold green]",
        border_style="green"
    ))
    
    query = state["query"]
    client = state["client"]
    context_id = state.get("context_id")
    task_id = state.get("task_id")
    
    if not client:
        console.print("   ❌ Error: No client available")
        return {"response": "Error: Client not initialized"}
    
    console.print(f"   📤 Query: [italic]{query}[/italic]")
    
    send_message_payload = {
        'message': {
            'role': 'user',
            'parts': [
                {'kind': 'text', 'text': query}
            ],
            'message_id': uuid4().hex,
        },
    }
    
    # Include context_id if this is a follow-up (don't reuse task_id - server creates new task)
    if context_id:
        send_message_payload['message']['context_id'] = context_id
        console.print(f"   🔄 Reusing context_id: {context_id[:16]}...")
    
    request = SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(**send_message_payload)
    )
    
    console.print("   ⏳ Waiting for response...")
    response = await client.send_message(request)
    
    # Extract response data using utility function
    task_id, context_id, result_text = extract_response_text(response)
    
    # Handle errors
    if result_text.startswith("Error:"):
        console.print(f"   ❌ {result_text}\n")
        return {
            "response": result_text,
            "all_responses": state.get("all_responses", []) + [result_text],
            "messages": state.get("messages", []) + [
                {"role": "user", "content": query},
                {"role": "assistant", "content": result_text}
            ]
        }
    
    if task_id:
        console.print(f"   ✅ Task created: task_id={task_id[:16]}...")
    if context_id:
        console.print(f"   ✅ Context ID: {context_id[:16]}...")
    console.print()  # Empty line before showing response
    
    # Store response text (empty string is valid, so check explicitly)
    if not result_text:
        result_text = "Response received but was empty"
    
    all_responses = state.get("all_responses", [])
    all_responses.append(result_text)
    
    return {
        "task_id": task_id,
        "context_id": context_id,
        "response": result_text,
        "all_responses": all_responses,
        "messages": state.get("messages", []) + [
            {"role": "user", "content": query},
            {"role": "assistant", "content": result_text}
        ]
    }


def ask_user_node(state: ClientAgentState) -> Dict[str, Any]:
    """Ask user if they want to refine the query or are satisfied."""
    console.print(Panel.fit(
        "[bold yellow]Step 2: Review Response[/bold yellow]",
        border_style="yellow"
    ))
    
    response = state.get("response", "")
    
    # Display full current response
    if response:
        console.print(f"\n   📄 Current Response:\n")
        console.print(Markdown(response))
        console.print("\n")
    
    # Ask user if they want to refine
    user_choice = console.input(
        "[bold cyan]   🤔 Do you want to ask a follow-up question?[/bold cyan] "
        "[dim](yes/no/refine)[/dim]: "
    ).strip().lower()
    
    if user_choice in ['yes', 'y', 'refine', 'r']:
        # User wants to refine
        new_query = console.input(
            "[bold cyan]   📝 Enter your follow-up question:[/bold cyan] "
        ).strip()
        
        if new_query:
            console.print(f"   ✅ Will refine with: {new_query}\n")
            return {
                "query": new_query,
                "user_wants_refinement": True,
            }
        else:
            console.print("   ⚠️  No query entered, proceeding to display\n")
            return {"user_wants_refinement": False}
    else:
        # User is satisfied
        console.print("   ✅ Proceeding to final display\n")
        return {"user_wants_refinement": False}


def should_continue(state: ClientAgentState) -> str:
    """Decision node: continue querying or display results."""
    if state.get("user_wants_refinement", False):
        return "continue"
    return "display"


def display_response_node(state: ClientAgentState) -> Dict[str, Any]:
    """Display the final response(s)."""
    console.print(Panel.fit(
        "[bold blue]Final Results[/bold blue]",
        border_style="blue"
    ))
    
    all_responses = state.get("all_responses", [])
    query = state.get("query", "")
    
    if all_responses:
        console.print(f"\n[bold]Research Topic:[/bold] {query}\n")
        
        # Display all responses
        for i, response in enumerate(all_responses, 1):
            console.print(f"[bold]Response {i}:[/bold]")
            console.print(Markdown(response))
            if i < len(all_responses):
                console.print("\n" + "─" * 60 + "\n")
    else:
        console.print("[yellow]No responses to display[/yellow]\n")
    
    # Create summary table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    table.add_row("Research Topic", query)
    table.add_row("Number of Responses", str(len(all_responses)))
    if state.get("task_id"):
        table.add_row("Task ID", state.get("task_id", "N/A")[:32] + "...")
    if state.get("context_id"):
        table.add_row("Context ID", state.get("context_id", "N/A")[:32] + "...")
    table.add_row("Status", "✅ Complete")
    
    console.print("\n")
    console.print(table)
    console.print("\n")
    
    return {}


def build_client_agent_graph():
    """Build the LangGraph for the client agent.
    
    Flow: send_query → ask_user → [continue: send_query] or [display: display] → END
    """
    graph = StateGraph(ClientAgentState)
    
    # Add nodes
    graph.add_node("send_query", send_query_node)
    graph.add_node("ask_user", ask_user_node)
    graph.add_node("display", display_response_node)
    
    # Set entry point
    graph.set_entry_point("send_query")
    
    # Add edges
    graph.add_edge("send_query", "ask_user")
    
    # Conditional edge: ask_user decides whether to continue or display
    graph.add_conditional_edges(
        "ask_user",
        should_continue,
        {
            "continue": "send_query",  # Loop back to send_query
            "display": "display"       # Go to display
        }
    )
    
    graph.add_edge("display", END)
    
    return graph.compile()


async def discover_agent(httpx_client: httpx.AsyncClient, base_url: str = "http://localhost:10000"):
    """Helper function to discover agent (used outside graph for efficiency)."""
    resolver = A2ACardResolver(
        httpx_client=httpx_client,
        base_url=base_url,
    )
    agent_card = await resolver.get_agent_card()
    a2a_client = A2AClient(
        httpx_client=httpx_client,
        agent_card=agent_card
    )
    return agent_card, a2a_client


async def main():
    """Main function to run the client agent with interactive loop."""
    console.print(Panel.fit(
        "[bold cyan]🤖 Research Assistant Agent - A2A Protocol Demo[/bold cyan]\n"
        "[dim]This agent discovers and communicates with the A2A server agent[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    base_url = "http://localhost:10000"
    
    # Create httpx client that will stay alive for the entire session
    httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
    
    try:
        # Step 1: Discover agent (ONCE - outside loop)
        console.print("[bold]🔍 Discovering server agent...[/bold]")
        try:
            agent_card, a2a_client = await discover_agent(httpx_client, base_url)
            console.print(f"[green]✅ Connected to: {agent_card.name}[/green]")
            console.print(f"[green]✅ Available skills: {', '.join([s.name for s in agent_card.skills])}[/green]\n")
        except Exception as e:
            console.print(f"[red]❌ Error discovering agent: {e}[/red]")
            console.print("[yellow]Make sure the server is running: uv run python -m app[/yellow]")
            return
        
        # Build graph once before the loop
        graph = build_client_agent_graph()
        
        # Step 2: Loop for research queries
        while True:
            query = console.input("\n[bold cyan]📝 Research topic[/bold cyan] (or 'quit' to exit): ")
            
            if query.lower() in ['quit', 'exit', 'q']:
                console.print("\n[bold]👋 Goodbye![/bold]\n")
                break
            
            if not query.strip():
                console.print("[yellow]Please enter a research topic.[/yellow]")
                continue
            
            # Run research workflow
            console.print(f"\n[bold]🔬 Researching:[/bold] {query}\n")
            
            try:
                result = await graph.ainvoke({
                    "query": query,
                    "base_url": base_url,
                    "agent_card": agent_card,  # Reuse discovered agent
                    "client": a2a_client,       # Reuse client
                    "httpx_client": httpx_client,  # Reuse httpx client
                    "task_id": None,
                    "context_id": None,
                    "response": None,
                    "all_responses": [],
                    "user_wants_refinement": None,
                    "messages": [],
                })
                
                console.print("\n[bold green]✅ Research complete![/bold green]\n")
                
            except Exception as e:
                console.print(f"\n[red]❌ Error during research: {e}[/red]")
                logger.exception("Error in research workflow")
    
    finally:
        # Cleanup
        await httpx_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())

