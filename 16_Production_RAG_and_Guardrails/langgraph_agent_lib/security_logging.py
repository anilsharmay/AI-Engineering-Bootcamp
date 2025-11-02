"""Security event logging for production-safe agents.

This module provides structured security event logging for monitoring,
auditing, and analysis of security-related events in agent workflows.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SecurityEventType(str, Enum):
    """Types of security events to log."""
    INPUT_REJECTED = "input_rejected"
    JAILBREAK_DETECTED = "jailbreak_detected"
    TOPIC_VIOLATION = "topic_violation"
    PII_DETECTED = "pii_detected"
    TOOL_OUTPUT_UNRELIABLE = "tool_output_unreliable"
    OUTPUT_REJECTED = "output_rejected"
    PROFANITY_DETECTED = "profanity_detected"
    REFINEMENT_ATTEMPT = "refinement_attempt"
    MAX_REFINEMENTS_REACHED = "max_refinements_reached"
    VALIDATION_ERROR = "validation_error"


def log_security_event(
    event_type: SecurityEventType,
    details: Dict[str, Any],
    state: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Log a security event for monitoring and analysis.
    
    This function creates structured security events that can be used for:
    - Security monitoring and alerting
    - Audit trails
    - Performance analysis
    - Threat detection patterns
    
    Args:
        event_type: Type of security event
        details: Event-specific details (message, error, execution_time, etc.)
        state: Optional agent state for additional context
        
    Returns:
        Security event dictionary with:
        - timestamp: ISO format timestamp
        - event_type: Type of event
        - details: Event-specific information
        - context: Additional state context if provided
    """
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type.value,
        "details": details,
    }
    
    # Add context from state if provided
    if state:
        context = {
            "validation_failures": state.get("validation_failures", 0),
            "message_count": len(state.get("messages", [])),
            "max_refinement_attempts": state.get("max_refinement_attempts", 0)
        }
        event["context"] = context
    
    # Log to Python logger with structured data
    log_message = f"SECURITY EVENT: {event_type.value}"
    if details.get("reason"):
        log_message += f" - {details.get('reason')}"
    
    logger.warning(
        log_message,
        extra={
            "security_event": event,
            "event_type": event_type.value
        }
    )
    
    return event

