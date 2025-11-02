"""Production-safe LangGraph agents with guardrails validation.

This module provides guarded agent implementations that validate inputs,
tool outputs, and agent responses using Guardrails AI.
"""

from typing import Dict, Any, List, Optional
import logging
import time

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from typing_extensions import TypedDict, Annotated

try:
    from guardrails import Guard
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False
    Guard = None  # type: ignore

from .agents import AgentState, get_default_tools
from .models import get_openai_model
from .rag import ProductionRAGChain
from .guardrails import (
    validate_input,
    validate_output,
    create_guardrails_guard,
    create_factuality_guard
)
from .security_logging import (
    log_security_event,
    SecurityEventType
)
from .validation_handlers import ValidationFailureHandler

logger = logging.getLogger(__name__)


def create_guards_for_agent(
    valid_topics: Optional[List[str]] = None,
    invalid_topics: Optional[List[str]] = None,
    enable_jailbreak: bool = True,
    enable_pii_protection: bool = True,
    enable_profanity: bool = True,
    enable_factuality: bool = True,
    factuality_eval_model: str = "gpt-4.1-mini",
    pii_entities: Optional[List[str]] = None
) -> Dict[str, Optional[Guard]]:
    """Create guards for guarded agent using guardrails.py utilities.
    
    This helper function leverages the guard utilities from guardrails.py to
    create properly configured guards for input, tool output, and output validation.
    
    Args:
        valid_topics: List of valid topics to allow (e.g., ["student loans", "financial aid"])
        invalid_topics: List of invalid topics to block (e.g., ["crypto", "gambling"])
        enable_jailbreak: Whether to enable jailbreak detection for inputs. Default: True
        enable_pii_protection: Whether to enable PII protection. Default: True
        enable_profanity: Whether to enable profanity filtering for outputs. Default: True
        enable_factuality: Whether to enable factuality checking for tool outputs. Default: True
        factuality_eval_model: Model to use for factuality evaluation. Default: "gpt-4.1-mini"
        pii_entities: List of PII entity types to detect. Default: Common PII types.
        
    Returns:
        Dictionary with keys:
        - 'input_guard': Guard for input validation (topic + jailbreak + PII)
        - 'tool_output_guard': Guard for tool output validation (factuality), or None
        - 'output_guard': Guard for output validation (profanity + PII)
        
    Raises:
        ImportError: If guardrails is not available
    """
    if not GUARDRAILS_AVAILABLE:
        raise ImportError(
            "Guardrails is not available. Install it with: pip install guardrails-ai"
        )
    
    guards = {}
    
    # Create input guard (topic + jailbreak + PII)
    # This validates user queries before agent processing
    input_guard = create_guardrails_guard(
        valid_topics=valid_topics,
        invalid_topics=invalid_topics,
        enable_jailbreak_detection=enable_jailbreak,
        enable_pii_protection=enable_pii_protection,
        enable_profanity_check=False,  # Profanity check only for outputs
        enable_competitor_check=False,
        pii_entities=pii_entities
    )
    guards['input_guard'] = input_guard
    logger.info("Input guard created: topic restriction, jailbreak detection, PII protection")
    
    # Create output guard (profanity + PII)
    # This validates agent responses before returning to user
    output_guard = create_guardrails_guard(
        valid_topics=None,  # Topic restriction only needed for input
        invalid_topics=None,
        enable_jailbreak_detection=False,  # Jailbreak only relevant for input
        enable_pii_protection=enable_pii_protection,  # Still check for PII leakage in output
        enable_profanity_check=enable_profanity,
        enable_competitor_check=False,
        pii_entities=pii_entities
    )
    guards['output_guard'] = output_guard
    logger.info("Output guard created: profanity check, PII protection")
    
    # Create factuality guard for tool outputs (especially RAG)
    # This validates tool responses for factual accuracy
    if enable_factuality:
        guards['tool_output_guard'] = create_factuality_guard(
            eval_model=factuality_eval_model,
            on_prompt=False  # Check on response, not prompt
        )
        logger.info(f"Tool output guard created: factuality check with {factuality_eval_model}")
    else:
        guards['tool_output_guard'] = None
        logger.info("Tool output guard: disabled")
    
    return guards


class GuardedAgentState(AgentState):
    """Extended state for guarded agents with validation tracking.
    
    Performance vs Security Trade-offs:
    - max_refinement_attempts: Higher = more retries but potential for loops
    """
    validation_results: Optional[List[Dict[str, Any]]] = []
    validation_failures: int = 0
    max_refinement_attempts: int = 3
    security_events: Optional[List[Dict[str, Any]]] = []  # Security event log
    guard_execution_times: Optional[Dict[str, float]] = {}  # Performance tracking


def create_input_validation_node(
    input_guard: Guard
):
    """Create an input validation node for user queries.
    
    Args:
        input_guard: Guard instance for input validation (jailbreak, topic, PII)
        
    Returns:
        Node function for LangGraph
    """
    def input_validation_node(state: GuardedAgentState) -> Dict[str, Any]:
        """Validate user input before agent processing."""
        messages = state.get("messages", [])
        validation_results = state.get("validation_results", [])
        security_events = state.get("security_events", [])
        guard_execution_times = state.get("guard_execution_times", {})
        
        if not messages:
            return {"validation_results": validation_results}
        
        # Get the last message (should be HumanMessage)
        last_message = messages[-1]
        
        if not isinstance(last_message, HumanMessage):
            # Not a user input, skip validation
            return {"validation_results": validation_results}
        
        try:
            logger.debug(f"Validating user input: {last_message.content[:100]}...")
            
            start_time = time.time()
            
            result = validate_input(
                input_guard,
                last_message.content,
                raise_on_failure=False  # We handle failures ourselves
            )
            
            execution_time = time.time() - start_time
            guard_execution_times["input_validation"] = execution_time
            
            validation_result = {
                "type": "input",
                "passed": result["validation_passed"],
                "message_preview": last_message.content[:100],
                "error": result.get("error"),
                "execution_time": execution_time
            }
            validation_results.append(validation_result)
            
            if not result["validation_passed"]:
                return ValidationFailureHandler.handle_input_validation_failure(
                    result=result,
                    state=state,
                    last_message=last_message,
                    execution_time=execution_time,
                    validation_results=validation_results,
                    security_events=security_events,
                    guard_execution_times=guard_execution_times
                )
            
            return {
                "validation_results": validation_results,
                "validation_failures": state.get("validation_failures", 0),
                "security_events": security_events,
                "guard_execution_times": guard_execution_times
            }
            
        except Exception as e:
            logger.error(f"Input validation error: {e}", exc_info=True)
            validation_result = {
                "type": "input",
                "passed": False,
                "error": str(e)
            }
            validation_results.append(validation_result)
            
            # Log validation error event
            event_details = {
                "reason": str(e),
                "message_preview": last_message.content[:100] if messages else ""
            }
            security_event = log_security_event(
                SecurityEventType.VALIDATION_ERROR, 
                event_details, 
                state
            )
            security_events.append(security_event)
            
            error_msg = AIMessage(
                content="I encountered an error validating your input. Please try again."
            )
            return {
                "messages": [error_msg],
                "validation_results": validation_results,
                "security_events": security_events
            }
    
    return input_validation_node


def _extract_original_prompt_from_messages(messages: List, tool_call_id: Optional[str] = None) -> Optional[str]:
    """Extract the original user prompt from message history.
    
    First tries to extract from tool call arguments, then falls back to first HumanMessage.
    
    Args:
        messages: List of messages in the conversation
        tool_call_id: Optional tool call ID to find the specific query that triggered the tool
        
    Returns:
        Original prompt string, or None if not found
    """
    # Try to extract from tool call arguments first
    if tool_call_id:
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls'):
                for tool_call in msg.tool_calls:
                    if tool_call.get('id') == tool_call_id:
                        args = tool_call.get('args', {})
                        query = args.get('query') or args.get('question')
                        if query:
                            return query
    
    # Fallback: use first HumanMessage
    for msg in messages:
        if isinstance(msg, HumanMessage):
            return msg.content
    
    return None


def create_tool_output_validation_node(
    factuality_guard: Optional[Guard] = None,
    rag_chain: Optional[ProductionRAGChain] = None
):
    """Create a tool output validation node, especially for RAG responses.
    
    Args:
        factuality_guard: Guard for factuality checking (required for RAG)
        rag_chain: Optional RAG chain to extract context for factuality checks
        
    Returns:
        Node function for LangGraph
    """
    def tool_output_validation_node(state: GuardedAgentState) -> Dict[str, Any]:
        """Validate tool responses, especially RAG outputs."""
        messages = state.get("messages", [])
        validation_results = state.get("validation_results", [])
        security_events = state.get("security_events", [])
        guard_execution_times = state.get("guard_execution_times", {})
        
        if not messages:
            return {"validation_results": validation_results}
        
        last_message = messages[-1]
        if not isinstance(last_message, ToolMessage):
            return {"validation_results": validation_results}
        
        tool_output = last_message.content
        tool_name = getattr(last_message, 'name', 'unknown')
        
        # Check if this is a RAG tool that needs factuality validation
        is_rag_tool = (
            tool_name == 'retrieve_information' and
            factuality_guard is not None and
            rag_chain is not None
        )
        
        try:
            if is_rag_tool:
                # Validate RAG output for factuality
                start_time = time.time()
                
                # Extract original prompt for factuality guard
                tool_call_id = getattr(last_message, 'tool_call_id', None)
                original_prompt = _extract_original_prompt_from_messages(messages, tool_call_id)
                
                # Call factuality guard
                try:
                    metadata = {"context": tool_output}
                    if original_prompt:
                        metadata["original_prompt"] = original_prompt
                    
                    guard_result = factuality_guard.validate(tool_output, metadata=metadata)
                    validation_passed = guard_result.validation_passed
                    error = None
                except Exception as e:
                    # Handle validation exceptions gracefully
                    error = str(e)
                    validation_passed = False
                    
                    # Skip security event for known "original_prompt missing" configuration issues
                    if "original_prompt" in error.lower():
                        logger.debug(f"Factuality guard configuration issue (expected): {error}")
                        validation_passed = True  # Allow through, not a security issue
                
                execution_time = time.time() - start_time
                guard_execution_times["tool_output_validation"] = execution_time
                
                validation_result = {
                    "type": "tool_output",
                    "tool": tool_name,
                    "passed": validation_passed,
                    "message_preview": tool_output[:100],
                    "error": error,
                    "execution_time": execution_time
                }
                validation_results.append(validation_result)
                
                # If validation failed and it's a real security issue, handle it
                if not validation_passed and error and "original_prompt" not in error.lower():
                    return ValidationFailureHandler.handle_tool_output_validation_failure(
                        result={"validation_passed": False, "error": error},
                        state=state,
                        last_message=last_message,
                        execution_time=execution_time,
                        validation_results=validation_results,
                        security_events=security_events,
                        guard_execution_times=guard_execution_times
                    )
            else:
                # For non-RAG tools, just record validation (trust by default)
                validation_result = {
                    "type": "tool_output",
                    "tool": tool_name,
                    "passed": True,
                    "message_preview": tool_output[:100]
                }
                validation_results.append(validation_result)
            
            return {
                "validation_results": validation_results,
                "security_events": security_events,
                "guard_execution_times": guard_execution_times
            }
            
        except Exception as e:
            logger.error(f"Tool output validation error: {e}", exc_info=True)
            validation_result = {
                "type": "tool_output",
                "tool": tool_name,
                "passed": False,
                "error": str(e)
            }
            validation_results.append(validation_result)
            
            security_event = log_security_event(
                SecurityEventType.VALIDATION_ERROR,
                {"reason": str(e), "tool": tool_name},
                state
            )
            security_events.append(security_event)
            
            return {
                "validation_results": validation_results,
                "security_events": security_events
            }
    
    return tool_output_validation_node


def create_output_validation_node(
    output_guard: Guard,
    max_refinement_attempts: int = 3
):
    """Create an output validation node for agent responses.
    
    Args:
        output_guard: Guard for output validation (content, profanity, PII)
        max_refinement_attempts: Maximum number of refinement attempts
        
    Returns:
        Node function for LangGraph
    """
    def output_validation_node(state: GuardedAgentState) -> Dict[str, Any]:
        """Validate agent output before returning to user."""
        messages = state.get("messages", [])
        validation_results = state.get("validation_results", [])
        validation_failures = state.get("validation_failures", 0)
        security_events = state.get("security_events", [])
        guard_execution_times = state.get("guard_execution_times", {})
        max_attempts = state.get("max_refinement_attempts", max_refinement_attempts)
        
        if not messages:
            return {"validation_results": validation_results}
        
        # Get the last message (should be AIMessage)
        last_message = messages[-1]
        
        if not isinstance(last_message, AIMessage):
            # Not an agent response, skip validation
            return {"validation_results": validation_results}
        
        # Skip validation messages (like HELPFULNESS:Y)
        if hasattr(last_message, 'content') and (
            "HELPFULNESS:" in str(last_message.content) or
            "VALIDATION:" in str(last_message.content)
        ):
            return {"validation_results": validation_results}
        
        try:
            agent_response = last_message.content
            logger.debug(f"Validating agent output: {agent_response[:100]}...")
            
            start_time = time.time()
            
            result = validate_output(
                output_guard,
                agent_response,
                raise_on_failure=False
            )
            
            execution_time = time.time() - start_time
            guard_execution_times["output_validation"] = execution_time
            
            validation_result = {
                "type": "output",
                "passed": result["validation_passed"],
                "message_preview": agent_response[:100],
                "error": result.get("error"),
                "execution_time": execution_time
            }
            validation_results.append(validation_result)
            
            if not result["validation_passed"]:
                logger.warning(f"Output validation failed: {result.get('error')}")
                
                failure_result = ValidationFailureHandler.handle_output_validation_failure(
                    result=result,
                    state=state,
                    agent_response=agent_response,
                    execution_time=execution_time,
                    validation_failures=validation_failures,
                    max_attempts=max_attempts,
                    validation_results=validation_results,
                    security_events=security_events,
                    guard_execution_times=guard_execution_times
                )
                
                if failure_result is not None:
                    # Max attempts reached, block the response
                    return failure_result
                else:
                    # Refinement needed, update validation_failures for state update
                    validation_failures += 1
            
            return {
                "validation_results": validation_results,
                "validation_failures": validation_failures,
                "security_events": security_events,
                "guard_execution_times": guard_execution_times
            }
            
        except Exception as e:
            logger.error(f"Output validation error: {e}", exc_info=True)
            validation_result = {
                "type": "output",
                "passed": False,
                "error": str(e)
            }
            validation_results.append(validation_result)
            
            # Log validation error event
            event_details = {
                "reason": str(e),
                "message_preview": agent_response[:100] if messages else ""
            }
            security_event = log_security_event(
                SecurityEventType.VALIDATION_ERROR,
                event_details,
                state
            )
            security_events.append(security_event)
            
            return {
                "validation_results": validation_results,
                "security_events": security_events
            }
    
    return output_validation_node


def route_after_input_validation(state: GuardedAgentState) -> str:
    """Route after input validation: reject or continue to agent."""
    validation_results = state.get("validation_results", [])
    
    if validation_results:
        last_result = validation_results[-1]
        if last_result.get("type") == "input" and not last_result.get("passed", True):
            # Input validation failed, check if error message was added
            messages = state.get("messages", [])
            if messages and isinstance(messages[-1], AIMessage):
                # Error message was added, end
                return END
            # Otherwise continue (should not normally reach here)
    
    return "agent"


def route_after_tool_validation(state: GuardedAgentState) -> str:
    """Route after tool validation: always continue to agent."""
    return "agent"


def route_after_output_validation(state: GuardedAgentState) -> str:
    """Route after output validation: pass, refine, or reject."""
    validation_results = state.get("validation_results", [])
    validation_failures = state.get("validation_failures", 0)
    max_attempts = state.get("max_refinement_attempts", 3)
    
    if validation_results:
        last_result = validation_results[-1]
        if last_result.get("type") == "output" and not last_result.get("passed", True):
            if validation_failures < max_attempts:
                # Attempt refinement
                logger.info(f"Output validation failed, attempting refinement ({validation_failures}/{max_attempts})")
                return "refine"
            else:
                # Max attempts reached, end
                logger.warning(f"Max refinement attempts ({max_attempts}) reached")
                return END
    
    # Validation passed or not applicable
    return END


def create_refinement_node():
    """Create a node that adds refinement feedback to the state."""
    def refinement_node(state: GuardedAgentState) -> Dict[str, Any]:
        """Add refinement feedback message to guide agent improvement."""
        validation_results = state.get("validation_results", [])
        messages = state.get("messages", [])
        
        if validation_results:
            last_result = validation_results[-1]
            error = last_result.get("error", "Response did not meet safety guidelines")
            
            refinement_feedback = HumanMessage(
                content=f"Previous response was rejected: {error}. Please provide a more appropriate, safe, and accurate response."
            )
            
            return {"messages": [refinement_feedback]}
        
        return {}
    
    return refinement_node


def create_guarded_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None,
    input_guard: Optional[Guard] = None,
    tool_output_guard: Optional[Guard] = None,
    output_guard: Optional[Guard] = None,
    max_refinement_attempts: int = 3
):
    """Create a production-safe LangGraph agent with guardrails validation.
    
    Performance vs Security Trade-offs:
    
    1. max_refinement_attempts (1-5 recommended):
       - Higher: More retries, better chance of success but slower
       - Lower: Faster failure, prevents infinite loops
       - Trade-off: Quality (high) vs Performance (low)
       - Recommendation: Use 3 for balanced approach
    
    2. Guard Selection:
       - More guards = Better security but slower execution
       - Fewer guards = Faster but less protection
       - Recommendation: Enable all for production, disable non-critical for dev
    
    Security Event Logging:
    - All security events are logged to state['security_events']
    - Events include: jailbreak attempts, PII detection, topic violations, etc.
    - Use for monitoring, auditing, and threat detection
    
    Performance Tracking:
    - Guard execution times are automatically tracked in state['guard_execution_times']
    - Used for monitoring and optimization analysis
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain for factuality checking
        input_guard: Guard for input validation (jailbreak, topic, PII)
        tool_output_guard: Guard for tool output validation (factuality)
        output_guard: Guard for output validation (content, profanity)
        max_refinement_attempts: Maximum refinement attempts for failed outputs
        
    Returns:
        Compiled LangGraph agent with guardrails
        
    Raises:
        ImportError: If guardrails is not available
    """
    if not GUARDRAILS_AVAILABLE:
        raise ImportError(
            "Guardrails is not available. Install it with: pip install guardrails-ai"
        )
    
    if tools is None:
        tools = get_default_tools(rag_chain)
    
    # Get model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(tools)
    
    def call_model(state: GuardedAgentState) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: GuardedAgentState):
        """Route to tools if the last message has tool calls."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        return "output_validation"  # Go to output validation if no tool calls
    
    # Build graph
    graph = StateGraph(GuardedAgentState)
    tool_node = ToolNode(tools)
    
    # Add core nodes
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    
    # Add validation nodes if guards provided
    if input_guard:
        graph.add_node(
            "input_validation",
            create_input_validation_node(
                input_guard
            )
        )
        graph.set_entry_point("input_validation")
        graph.add_conditional_edges(
            "input_validation",
            route_after_input_validation,
            {"agent": "agent", END: END}
        )
    else:
        graph.set_entry_point("agent")
    
    # Tool execution routing
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"action": "action", "output_validation": "output_validation"}
    )
    
    # Tool output validation (if guard provided)
    if tool_output_guard:
        graph.add_node(
            "tool_output_validation",
            create_tool_output_validation_node(
                tool_output_guard, 
                rag_chain
            )
        )
        graph.add_edge("action", "tool_output_validation")
        graph.add_edge("tool_output_validation", "agent")
    else:
        graph.add_edge("action", "agent")
    
    # Output validation (if guard provided)
    if output_guard:
        graph.add_node(
            "output_validation",
            create_output_validation_node(
                output_guard, 
                max_refinement_attempts
            )
        )
        graph.add_conditional_edges(
            "output_validation",
            route_after_output_validation,
            {"refine": "refinement", END: END}
        )
        
        # Refinement loop
        graph.add_node("refinement", create_refinement_node())
        graph.add_edge("refinement", "agent")
    else:
        # If no output guard, handle routing after agent response
        # We need to update should_continue to handle this case
        def should_continue_fallback(state: GuardedAgentState):
            last_message = state["messages"][-1]
            if getattr(last_message, "tool_calls", None):
                return "action"
            return END
        
        graph.add_conditional_edges(
            "agent",
            should_continue_fallback,
            {"action": "action", END: END}
        )
    
    return graph.compile()

