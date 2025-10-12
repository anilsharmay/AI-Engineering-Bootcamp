"""Utility functions for tracking and analyzing research configuration metrics."""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from langsmith import Client


def get_research_metrics(
    project_name: Optional[str] = None,
    hours_back: int = 24,
    run_tag: str = "research-config"
) -> Dict[str, Dict]:
    """
    Fetch research configuration metrics from LangSmith.
    
    Args:
        project_name: LangSmith project name (defaults to LANGCHAIN_PROJECT env var)
        hours_back: How many hours back to search for runs
        run_tag: Tag to filter research configuration runs
        
    Returns:
        Dictionary mapping configuration names to performance metrics
    """
    client = Client()
    
    # Use environment variable if not specified
    if project_name is None:
        project_name = os.getenv("LANGCHAIN_PROJECT", "default")
    
    # Calculate time window
    since = datetime.now() - timedelta(hours=hours_back)
    
    # Fetch runs
    runs = list(client.list_runs(
        project_name=project_name,
        start_time=since,
        filter=f'has(tags, "{run_tag}")',
        limit=50
    ))
    
    # Parse metrics by configuration name
    metrics = {}
    for run in runs:
        if not run.end_time:
            continue
            
        # Extract metadata
        metadata = run.extra.get("metadata", {}) if run.extra else {}
        config_name = metadata.get("configuration_name")
        
        if config_name:
            duration = (run.end_time - run.start_time).total_seconds()
            
            metrics[config_name] = {
                "duration_seconds": round(duration, 1),
                "total_tokens": run.total_tokens or 0,
                "prompt_tokens": run.prompt_tokens or 0,
                "completion_tokens": run.completion_tokens or 0,
                "total_cost": run.total_cost or 0,
                "status": run.status,
                "run_id": str(run.id),
                "start_time": run.start_time.isoformat() if run.start_time else None
            }
    
    return metrics


def create_metrics_comparison_table(metrics: Dict[str, Dict]) -> pd.DataFrame:
    """
    Create a formatted comparison table from research metrics.
    
    Args:
        metrics: Dictionary from get_research_metrics()
        
    Returns:
        Pandas DataFrame with formatted comparison
    """
    rows = []
    for config_name, data in metrics.items():
        rows.append({
            "Configuration": config_name,
            "Duration (s)": data["duration_seconds"],
            "Duration (min)": round(data["duration_seconds"] / 60, 1),
            "Total Tokens": f"{data['total_tokens']:,}",
            "Prompt Tokens": f"{data['prompt_tokens']:,}",
            "Completion Tokens": f"{data['completion_tokens']:,}",
            "Cost": f"${data['total_cost']:.2f}",
            "Status": data["status"]
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by configuration name for consistent ordering
    df = df.sort_values("Configuration")
    
    return df


def print_metrics_summary(metrics: Dict[str, Dict]) -> None:
    """
    Print a formatted metrics summary to console.
    
    Args:
        metrics: Dictionary from get_research_metrics()
    """
    print("RESEARCH CONFIGURATION METRICS (from LangSmith)")
    print("=" * 70)
    
    total_cost = 0
    total_tokens = 0
    total_time = 0
    
    for config_name, data in sorted(metrics.items()):
        print(f"\n{config_name}:")
        print(f"  Duration: {data['duration_seconds']:.1f}s ({data['duration_seconds']/60:.1f}min)")
        print(f"  Tokens: {data['total_tokens']:,} ({data['prompt_tokens']:,} prompt + {data['completion_tokens']:,} completion)")
        print(f"  Cost: ${data['total_cost']:.2f}")
        print(f"  Status: {data['status']}")
        
        total_cost += data['total_cost']
        total_tokens += data['total_tokens']
        total_time += data['duration_seconds']
    
    print("\n" + "=" * 70)
    print(f"TOTAL ACROSS {len(metrics)} CONFIGURATIONS:")
    print(f"  Time: {total_time:.1f}s ({total_time/60:.1f}min)")
    print(f"  Tokens: {total_tokens:,}")
    print(f"  Cost: ${total_cost:.2f}")
    print("=" * 70)


def get_langsmith_url(project_name: Optional[str] = None) -> str:
    """
    Get the LangSmith URL for viewing runs.
    
    Args:
        project_name: LangSmith project name
        
    Returns:
        URL string
    """
    if project_name is None:
        project_name = os.getenv("LANGCHAIN_PROJECT", "default")
    
    return f"https://smith.langchain.com/o/{project_name}"


def fetch_and_display_metrics(
    project_name: Optional[str] = None,
    hours_back: int = 24
) -> pd.DataFrame:
    """
    Convenience function to fetch and display research metrics in one call.
    
    Args:
        project_name: LangSmith project name
        hours_back: How many hours back to search
        
    Returns:
        DataFrame with metrics comparison
    """
    print("Fetching research configuration data from LangSmith...")
    
    metrics = get_research_metrics(project_name, hours_back)
    
    if not metrics:
        print("No research configuration runs found.")
        print(f"Make sure runs are tagged with 'research-config' and within last {hours_back} hours.")
        return pd.DataFrame()
    
    print(f"Found {len(metrics)} research configurations\n")
    
    # Print summary
    print_metrics_summary(metrics)
    
    print(f"\nView detailed traces at: {get_langsmith_url(project_name)}")
    
    # Create and return table
    df = create_metrics_comparison_table(metrics)
    
    print("\nDETAILED COMPARISON:")
    print("=" * 70)
    
    return df


def calculate_cost_breakdown(
    total_cost: float,
    prompt_tokens: int,
    completion_tokens: int,
    input_cost_per_1m: float = 3.00,
    output_cost_per_1m: float = 15.00
) -> Dict[str, float]:
    """
    Break down research costs by input/output tokens.
    
    Args:
        total_cost: Total cost from LangSmith
        prompt_tokens: Input token count
        completion_tokens: Output token count
        input_cost_per_1m: Cost per million input tokens (Claude Sonnet 4 default)
        output_cost_per_1m: Cost per million output tokens (Claude Sonnet 4 default)
        
    Returns:
        Dictionary with cost breakdown
    """
    input_cost = (prompt_tokens / 1_000_000) * input_cost_per_1m
    output_cost = (completion_tokens / 1_000_000) * output_cost_per_1m
    
    return {
        "input_cost": round(input_cost, 2),
        "output_cost": round(output_cost, 2),
        "calculated_total": round(input_cost + output_cost, 2),
        "actual_total": total_cost,
        "difference": round(abs(total_cost - (input_cost + output_cost)), 2)
    }


def compare_configurations(metrics: Dict[str, Dict]) -> Dict[str, str]:
    """
    Analyze metrics to determine which configuration performs best in different dimensions.
    
    Args:
        metrics: Dictionary from get_research_metrics()
        
    Returns:
        Dictionary with performance winners in each category
    """
    if not metrics:
        return {}
    
    # Find best performers
    fastest = min(metrics.items(), key=lambda x: x[1]['duration_seconds'])
    cheapest = min(metrics.items(), key=lambda x: x[1]['total_cost'])
    most_comprehensive = max(metrics.items(), key=lambda x: x[1]['total_tokens'])
    
    # Calculate efficiency metrics
    efficiency_scores = {}
    for name, data in metrics.items():
        if data['duration_seconds'] > 0 and data['total_cost'] > 0:
            # Tokens per second (throughput)
            throughput = data['total_tokens'] / data['duration_seconds']
            # Tokens per dollar (cost efficiency)
            cost_efficiency = data['total_tokens'] / data['total_cost']
            efficiency_scores[name] = {
                'throughput': throughput,
                'cost_efficiency': cost_efficiency
            }
    
    most_efficient = max(efficiency_scores.items(), key=lambda x: x[1]['cost_efficiency']) if efficiency_scores else (None, None)
    
    return {
        "fastest": fastest[0],
        "fastest_time": f"{fastest[1]['duration_seconds']:.1f}s",
        "cheapest": cheapest[0],
        "cheapest_cost": f"${cheapest[1]['total_cost']:.2f}",
        "most_comprehensive": most_comprehensive[0],
        "most_comprehensive_tokens": f"{most_comprehensive[1]['total_tokens']:,}",
        "most_cost_efficient": most_efficient[0] if most_efficient[0] else "N/A",
    }

