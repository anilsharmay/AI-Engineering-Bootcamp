"""Utility functions for visualizing graph execution and traversal patterns."""

from collections import Counter
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


def visualize_graph_traversal(
    experiment_results: List[Tuple[str, Dict]],
    figsize: Tuple[int, int] = (16, 6)
) -> None:
    """
    Create visualizations comparing graph traversal across experiments.
    
    Args:
        experiment_results: List of (experiment_name, result_dict) tuples
        figsize: Figure size for matplotlib plots
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Chart 1: Total Node Visit Counts
    _plot_node_visit_counts(ax1, experiment_results)
    
    # Chart 2: Node Type Frequency Distribution
    _plot_node_type_frequency(ax2, experiment_results)
    
    plt.tight_layout()
    plt.show()


def _plot_node_visit_counts(ax, experiment_results: List[Tuple[str, Dict]]) -> None:
    """Plot total number of nodes visited per experiment."""
    node_counts = {exp_name: result['nodes_visited'] for exp_name, result in experiment_results}
    
    # Color mapping for consistency
    colors_map = {'Parallel': '#1f77b4', 'Deep': '#ff7f0e', 'No Clarify': '#2ca02c'}
    colors = [colors_map.get(name, '#gray') for name in node_counts.keys()]
    
    ax.barh(list(node_counts.keys()), list(node_counts.values()), color=colors)
    ax.set_xlabel('Total Nodes Visited')
    ax.set_title('Graph Traversal Complexity')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (name, count) in enumerate(node_counts.items()):
        ax.text(count + 0.1, i, str(count), va='center', fontsize=10)


def _plot_node_type_frequency(ax, experiment_results: List[Tuple[str, Dict]]) -> None:
    """Plot stacked bar chart showing frequency of each node type."""
    # Node type mapping for display names
    node_type_map = {
        "clarify_with_user": "clarify",
        "write_research_brief": "brief",
        "research_supervisor": "supervisor",
        "final_report_generation": "report"
    }
    
    # Count actual node visits per experiment
    node_visit_data = {}
    for exp_name, result in experiment_results:
        sequence = result.get('node_sequence', [])
        counts = Counter(sequence)
        node_visit_data[exp_name] = {
            node_type_map.get(node, node): count 
            for node, count in counts.items()
        }
    
    # Get all unique node types
    all_node_types = set()
    for data in node_visit_data.values():
        all_node_types.update(data.keys())
    all_node_types = sorted(all_node_types)
    
    # Create stacked horizontal bar chart
    y_positions = np.arange(len(experiment_results))
    bar_width = 0.6
    bottoms = np.zeros(len(experiment_results))
    
    for node_type in all_node_types:
        values = [node_visit_data[exp[0]].get(node_type, 0) for exp in experiment_results]
        ax.barh(y_positions, values, bar_width, left=bottoms, label=node_type, alpha=0.8)
        bottoms += values
    
    ax.set_yticks(y_positions)
    ax.set_yticklabels([exp[0] for exp in experiment_results])
    ax.set_xlabel('Node Visits (Actual Count)')
    ax.set_title('Actual Node Execution Frequency')
    ax.legend(title="Node Type", loc='upper right')
    ax.grid(axis='x', alpha=0.3)


def print_execution_sequences(experiment_results: List[Tuple[str, Dict]]) -> None:
    """
    Print detailed execution sequences for each experiment.
    
    Args:
        experiment_results: List of (experiment_name, result_dict) tuples
    """
    print("\nACTUAL EXECUTION SEQUENCES:")
    print("=" * 70)
    
    for exp_name, result in experiment_results:
        sequence = result.get('node_sequence', [])
        
        print(f"\n{exp_name}:")
        
        if sequence:
            print(f"  Path: START → {' → '.join(sequence)} → END")
            
            # Check for repeated nodes (iterations/loops)
            node_counts = Counter(sequence)
            repeated = {node: count for node, count in node_counts.items() if count > 1}
            if repeated:
                print(f"  Iterations detected:")
                for node, count in repeated.items():
                    print(f"    - {node}: visited {count} times")
        else:
            print(f"  Path: No sequence data captured")
        
        print(f"  Total nodes: {result['nodes_visited']}")
        print(f"  Duration: {result['duration_seconds']}s ({result['duration_minutes']}min)")
        print(f"  Config: {result['config']['parallel']}P / {result['config']['iterations']}I / {result['config']['tool_calls']}T")


def analyze_execution_differences(experiment_results: List[Tuple[str, Dict]]) -> None:
    """
    Analyze and print differences in execution paths.
    
    Args:
        experiment_results: List of (experiment_name, result_dict) tuples
    """
    print("\n" + "=" * 70)
    print("EXECUTION PATH ANALYSIS:")
    print("=" * 70)
    
    # Collect all sequences
    sequences = {exp_name: result.get('node_sequence', []) for exp_name, result in experiment_results}
    
    # Find unique vs common nodes
    all_nodes = set()
    for seq in sequences.values():
        all_nodes.update(seq)
    
    print(f"\nUnique nodes across all experiments: {', '.join(sorted(all_nodes))}")
    
    # Compare paths
    print("\nPath Differences:")
    
    exp_names = [exp[0] for exp in experiment_results]
    for i, exp1_name in enumerate(exp_names):
        for exp2_name in exp_names[i+1:]:
            seq1 = sequences[exp1_name]
            seq2 = sequences[exp2_name]
            
            if seq1 == seq2:
                print(f"  {exp1_name} vs {exp2_name}: Identical path")
            else:
                diff1 = set(seq1) - set(seq2)
                diff2 = set(seq2) - set(seq1)
                
                if diff1:
                    print(f"  {exp1_name} has: {', '.join(diff1)}")
                if diff2:
                    print(f"  {exp2_name} has: {', '.join(diff2)}")
                
                # Count differences
                if len(seq1) != len(seq2):
                    print(f"  Length difference: {exp1_name}={len(seq1)} vs {exp2_name}={len(seq2)}")
    
    print("\nKey Observations:")
    print("  - Configurations may traverse the same nodes but different frequencies")
    print("  - 'Deep' config typically shows more supervisor iterations")
    print("  - 'No Clarify' may skip clarification node entirely")
    print("=" * 70)


def visualize_single_experiment(experiment_name: str, result: Dict) -> None:
    """
    Visualize a single experiment execution immediately after completion.
    
    Args:
        experiment_name: Name of the experiment
        result: Result dictionary from run_research_config
    """
    print(f"\n{'='*70}")
    print(f"EXECUTION ANALYSIS: {experiment_name}")
    print(f"{'='*70}")
    
    sequence = result.get('node_sequence', [])
    
    if sequence:
        print(f"\nExecution Path:")
        print(f"  START → {' → '.join(sequence)} → END")
        print(f"\nNode Statistics:")
        print(f"  Total nodes visited: {result['nodes_visited']}")
        
        # Check for iterations
        node_counts = Counter(sequence)
        repeated = {node: count for node, count in node_counts.items() if count > 1}
        if repeated:
            print(f"\n  Iterations detected:")
            for node, count in repeated.items():
                print(f"    - {node}: {count} times")
        else:
            print(f"  No iterations (linear execution)")
    else:
        print("\n  No execution sequence captured")
    
    print(f"\nPerformance:")
    print(f"  Duration: {result['duration_seconds']}s ({result['duration_minutes']}min)")
    print(f"  Configuration: {result['config']['parallel']}P / {result['config']['iterations']}I / {result['config']['tool_calls']}T")
    print(f"{'='*70}\n")


def visualize_and_analyze_execution(experiment_results: List[Tuple[str, Dict]]) -> None:
    """
    Convenience function to run all visualization and analysis.
    
    Args:
        experiment_results: List of (experiment_name, result_dict) tuples
    """
    # Create visualizations
    visualize_graph_traversal(experiment_results)
    
    # Print sequences
    print_execution_sequences(experiment_results)
    
    # Analyze differences
    analyze_execution_differences(experiment_results)

