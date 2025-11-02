"""Validation failure handlers for guarded agents.

This module provides utilities for handling validation failures consistently
across all validation nodes in guarded agent workflows.
"""

from typing import Dict, Any, List, Optional
import logging

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from .security_logging import (
    log_security_event,
    SecurityEventType
)

logger = logging.getLogger(__name__)

# Type alias to avoid circular imports
GuardedAgentState = Dict[str, Any]


class ValidationFailureHandler:
    """Utility class for handling validation failures consistently across all validation nodes.
    
    This class centralizes the logic for:
    - Determining security event types based on validation errors
    - Logging security events and updating state
    - Creating appropriate error messages
    """
    
    @staticmethod
    def determine_input_event_type(error_str: str) -> SecurityEventType:
        """Determine security event type for input validation failures."""
        error_lower = error_str.lower()
        if "jailbreak" in error_lower:
            return SecurityEventType.JAILBREAK_DETECTED
        elif "topic" in error_lower or "invalid" in error_lower:
            return SecurityEventType.TOPIC_VIOLATION
        elif "pii" in error_lower or "credit" in error_lower or "ssn" in error_lower:
            return SecurityEventType.PII_DETECTED
        else:
            return SecurityEventType.INPUT_REJECTED
    
    @staticmethod
    def determine_output_event_type(error_str: str) -> SecurityEventType:
        """Determine security event type for output validation failures."""
        error_lower = error_str.lower()
        if "profanity" in error_lower:
            return SecurityEventType.PROFANITY_DETECTED
        elif "pii" in error_lower or "credit" in error_lower or "ssn" in error_lower:
            return SecurityEventType.PII_DETECTED
        else:
            return SecurityEventType.OUTPUT_REJECTED
    
    @staticmethod
    def handle_input_validation_failure(
        result: Dict[str, Any],
        state: GuardedAgentState,
        last_message: HumanMessage,
        execution_time: float,
        validation_results: List[Dict[str, Any]],
        security_events: List[Dict[str, Any]],
        guard_execution_times: Dict[str, float]
    ) -> Dict[str, Any]:
        """Handle input validation failure by logging event and returning error response.
        
        Args:
            result: Validation result dictionary with 'error' key
            state: Current agent state
            last_message: The human message that failed validation
            execution_time: Time taken for validation
            validation_results: List to append validation result to
            security_events: List to append security event to
            guard_execution_times: Dict to update with execution time
            
        Returns:
            State update dictionary with error message
        """
        validation_failures = state.get("validation_failures", 0) + 1
        
        # Determine event type
        error_str = result.get("error", "")
        event_type = ValidationFailureHandler.determine_input_event_type(error_str)
        
        # Log security event
        event_details = {
            "reason": result.get("error", "Input validation failed"),
            "message_preview": last_message.content[:100],
            "execution_time": execution_time
        }
        security_event = log_security_event(event_type, event_details, state)
        security_events.append(security_event)
        
        # Create error message
        error_msg = AIMessage(
            content=f"I'm sorry, but I cannot process that request. {result.get('error', 'Input validation failed.')} Please rephrase your question about student loans."
        )
        logger.warning(f"Input validation failed: {result.get('error')}")
        
        return {
            "messages": [error_msg],
            "validation_results": validation_results,
            "validation_failures": validation_failures,
            "security_events": security_events,
            "guard_execution_times": guard_execution_times
        }
    
    @staticmethod
    def handle_tool_output_validation_failure(
        result: Dict[str, Any],
        state: GuardedAgentState,
        last_message: ToolMessage,
        execution_time: float,
        validation_results: List[Dict[str, Any]],
        security_events: List[Dict[str, Any]],
        guard_execution_times: Dict[str, float]
    ) -> Dict[str, Any]:
        """Handle tool output validation failure by logging event and returning warning.
        
        Args:
            result: Validation result dictionary with 'error' key
            state: Current agent state
            last_message: The tool message that failed validation
            execution_time: Time taken for validation
            validation_results: List to append validation result to
            security_events: List to append security event to
            guard_execution_times: Dict to update with execution time
            
        Returns:
            State update dictionary with warning message
        """
        tool_output = last_message.content
        
        # Log security event
        event_details = {
            "reason": result.get("error", "Tool output factuality check failed"),
            "tool": "rag",
            "message_preview": tool_output[:100],
            "execution_time": execution_time
        }
        security_event = log_security_event(
            SecurityEventType.TOOL_OUTPUT_UNRELIABLE,
            event_details,
            state
        )
        security_events.append(security_event)
        
        # Replace tool output with warning
        warning_msg = ToolMessage(
            content="Warning: The retrieved information may not be fully reliable. Please verify details.",
            tool_call_id=last_message.tool_call_id,
            name=last_message.name
        )
        
        return {
            "messages": [warning_msg],
            "validation_results": validation_results,
            "security_events": security_events,
            "guard_execution_times": guard_execution_times
        }
    
    @staticmethod
    def handle_output_validation_failure(
        result: Dict[str, Any],
        state: GuardedAgentState,
        agent_response: str,
        execution_time: float,
        validation_failures: int,
        max_attempts: int,
        validation_results: List[Dict[str, Any]],
        security_events: List[Dict[str, Any]],
        guard_execution_times: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """Handle output validation failure by logging event and determining next action.
        
        Args:
            result: Validation result dictionary with 'error' key
            state: Current agent state
            agent_response: The agent response that failed validation
            execution_time: Time taken for validation
            validation_failures: Current count of validation failures
            max_attempts: Maximum refinement attempts allowed
            validation_results: List to append validation result to
            security_events: List to append security event to
            guard_execution_times: Dict to update with execution time
            
        Returns:
            State update dictionary if max attempts reached (blocks), None if refinement needed
        """
        validation_failures += 1
        
        # Determine event type
        error_str = result.get("error", "")
        event_type = ValidationFailureHandler.determine_output_event_type(error_str)
        
        # Log security event
        event_details = {
            "reason": result.get("error", "Output validation failed"),
            "message_preview": agent_response[:100],
            "execution_time": execution_time,
            "refinement_attempt": validation_failures,
            "max_attempts": max_attempts
        }
        security_event = log_security_event(event_type, event_details, state)
        security_events.append(security_event)
        
        if validation_failures >= max_attempts:
            # Max refinements reached, return safe message
            event_details_max = {
                "reason": "Maximum refinement attempts reached",
                "attempts": validation_failures,
                "max_attempts": max_attempts
            }
            security_event_max = log_security_event(
                SecurityEventType.MAX_REFINEMENTS_REACHED,
                event_details_max,
                state
            )
            security_events.append(security_event_max)
            
            safe_msg = AIMessage(
                content="I apologize, but I'm unable to provide a response that meets safety guidelines. Please try rephrasing your question."
            )
            
            return {
                "messages": [safe_msg],
                "validation_results": validation_results,
                "validation_failures": validation_failures,
                "security_events": security_events,
                "guard_execution_times": guard_execution_times
            }
        else:
            # Log refinement attempt
            event_details_refine = {
                "reason": result.get("error", "Output validation failed"),
                "attempt": validation_failures,
                "max_attempts": max_attempts
            }
            security_event_refine = log_security_event(
                SecurityEventType.REFINEMENT_ATTEMPT,
                event_details_refine,
                state
            )
            security_events.append(security_event_refine)
            return None

