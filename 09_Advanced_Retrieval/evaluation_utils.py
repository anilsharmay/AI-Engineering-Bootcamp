"""
Utility functions for retriever evaluation.

Provides reusable evaluation logic with automatic LangSmith cost tracking.
"""

import time
import os
import pickle
from typing import Dict, Any, List
from langsmith import Client
from ragas import evaluate
from ragas.evaluation import EvaluationDataset
from ragas.metrics import context_precision, context_recall, context_entity_recall


def calculate_cost_from_run(run) -> float:
    """
    Calculate total cost from a LangSmith run.
    
    Args:
        run: LangSmith run object
        
    Returns:
        Total cost in USD
    """
    # OpenAI pricing (as of Oct 2024)
    GPT_4_1_NANO_INPUT = 0.10 / 1_000_000  # per token
    GPT_4_1_NANO_OUTPUT = 0.40 / 1_000_000
    TEXT_EMBEDDING_3_SMALL = 0.02 / 1_000_000
    
    # Cohere pricing
    COHERE_RERANK_V3_5 = 0.002 / 1_000  # per search
    
    total_cost = 0.0
    
    # Parse run tree for costs
    if hasattr(run, 'prompt_tokens') and hasattr(run, 'completion_tokens'):
        # LLM call
        total_cost += (run.prompt_tokens * GPT_4_1_NANO_INPUT)
        total_cost += (run.completion_tokens * GPT_4_1_NANO_OUTPUT)
    
    if hasattr(run, 'total_tokens') and 'embedding' in str(run.name).lower():
        # Embedding call
        total_cost += (run.total_tokens * TEXT_EMBEDDING_3_SMALL)
    
    # Check for Cohere rerank calls
    if 'rerank' in str(run.name).lower() or 'cohere' in str(run.name).lower():
        # Approximate: number of documents reranked
        total_cost += COHERE_RERANK_V3_5
    
    # Recursively sum child runs
    if hasattr(run, 'child_runs'):
        for child in run.child_runs:
            total_cost += calculate_cost_from_run(child)
    
    return total_cost


def get_evaluation_cost(start_time: float, end_time: float, project_name: str, wait_time: int = 5) -> float:
    """
    Get total cost for all LangSmith runs in a time window.
    
    Args:
        start_time: Unix timestamp of evaluation start
        end_time: Unix timestamp of evaluation end
        project_name: LangSmith project name
        wait_time: Seconds to wait for trace upload
        
    Returns:
        Total cost in USD for all runs in the time window
    """
    time.sleep(wait_time)  # Wait for traces to upload
    
    client = Client()
    
    try:
        from datetime import datetime
        
        # Convert unix timestamps to datetime
        start_dt = datetime.fromtimestamp(start_time)
        end_dt = datetime.fromtimestamp(end_time)
        
        # Get all runs in the time window
        runs = client.list_runs(
            project_name=project_name,
            start_time=start_dt,
            end_time=end_dt
        )
        
        # Sum costs from all runs
        total_cost = 0.0
        run_count = 0
        for run in runs:
            if run.total_cost is not None:
                # Convert to float (LangSmith returns Decimal)
                total_cost += float(run.total_cost)
                run_count += 1
        
        return total_cost
        
    except Exception as e:
        print(f"Warning: Could not retrieve cost from LangSmith: {e}")
        return 0.0


def evaluate_retriever_config(
    retriever,
    retriever_name: str,
    chunking_type: str,
    golden_dataset,
    llm=None,
    embeddings=None,
    project_name: str = "Advanced-Retrieval-Evaluation",
    auto_cost: bool = True,
    use_cache: bool = True,
    force_recompute: bool = False
) -> Dict[str, Any]:
    """
    Evaluate a single retriever configuration with automatic cost tracking and caching.
    
    Args:
        retriever: LangChain retriever instance
        retriever_name: Name of retriever (e.g., "Naive", "BM25")
        chunking_type: Type of chunking (e.g., "Standard", "Semantic")
        golden_dataset: Pandas DataFrame with columns: user_input/question, reference/ground_truth
        llm: LangChain LLM instance for Ragas metrics (optional, will use default if not provided)
        embeddings: LangChain embeddings instance for Ragas metrics (optional)
        project_name: LangSmith project name
        auto_cost: If True, automatically fetch cost from LangSmith
        use_cache: If True, use cached results if available
        force_recompute: If True, bypass cache and re-run evaluation
        
    Returns:
        Dict with metrics: precision, recall, entity_recall, latency, cost
    """
    # Check for cached results
    cache_dir = './eval_cache'
    cache_file = f"{cache_dir}/{retriever_name}_{chunking_type}.pkl"
    
    if use_cache and os.path.exists(cache_file) and not force_recompute:
        with open(cache_file, 'rb') as f:
            cached_result = pickle.load(f)
        
        # Display cached results
        print(f"\n{retriever_name} ({chunking_type}) [CACHED]:")
        print(f"  Precision: {cached_result['precision']:.3f}")
        print(f"  Recall: {cached_result['recall']:.3f}")
        print(f"  Entity Recall: {cached_result['entity_recall']:.3f}")
        print(f"  Latency: {cached_result['latency']:.2f}s")
        if 'cost' in cached_result and cached_result['cost'] > 0:
            print(f"  Cost: ${cached_result['cost']:.4f}")
        
        return cached_result
    
    # Retrieve contexts for all test questions
    # Ragas 0.2.10 uses 'user_input' for questions, 'reference' for ground truth
    retrieved_contexts = []
    start_time = time.time()
    
    question_col = 'user_input' if 'user_input' in golden_dataset.columns else 'question'
    ground_truth_col = 'reference' if 'reference' in golden_dataset.columns else 'ground_truth'
    
    for question in golden_dataset[question_col]:
        docs = retriever.invoke(question)
        contexts = [doc.page_content for doc in docs]
        retrieved_contexts.append(contexts)
    
    total_latency = time.time() - start_time
    
    # Prepare evaluation dataset
    # Convert to list of samples (ragas 0.2.10 format)
    # Field names: user_input, retrieved_contexts, reference
    samples = []
    questions = golden_dataset[question_col].tolist()
    ground_truths = golden_dataset[ground_truth_col].tolist()
    
    for i in range(len(questions)):
        samples.append({
            'user_input': questions[i],
            'retrieved_contexts': retrieved_contexts[i],
            'reference': ground_truths[i]
        })
    
    eval_dataset = EvaluationDataset.from_dict(samples)
    
    # Run Ragas evaluation
    # Pass llm and embeddings if provided, otherwise ragas will use defaults
    eval_params = {
        'dataset': eval_dataset,
        'metrics': [context_precision, context_recall, context_entity_recall],
        'show_progress': False
    }
    if llm is not None:
        eval_params['llm'] = llm
    if embeddings is not None:
        eval_params['embeddings'] = embeddings
    
    # Record evaluation start time for cost tracking
    eval_start_time = time.time()
    
    result = evaluate(**eval_params)
    
    # Record evaluation end time
    eval_end_time = time.time()
    
    # Extract metric values from EvaluationResult
    # Convert to dict or access as DataFrame
    if hasattr(result, 'to_pandas'):
        result_df = result.to_pandas()
        precision = result_df['context_precision'].mean() if 'context_precision' in result_df else 0.0
        recall = result_df['context_recall'].mean() if 'context_recall' in result_df else 0.0
        entity_recall = result_df['context_entity_recall'].mean() if 'context_entity_recall' in result_df else 0.0
    else:
        # Fallback: try accessing as dict
        precision = getattr(result, 'context_precision', 0.0)
        recall = getattr(result, 'context_recall', 0.0)
        entity_recall = getattr(result, 'context_entity_recall', 0.0)
    
    # Get cost from LangSmith if enabled
    cost = 0.0
    if auto_cost:
        cost = get_evaluation_cost(eval_start_time, eval_end_time, project_name)
    
    # Display results
    print(f"\n{retriever_name} ({chunking_type}):")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")
    print(f"  Entity Recall: {entity_recall:.3f}")
    print(f"  Latency: {total_latency:.2f}s")
    if auto_cost:
        print(f"  Cost: ${cost:.4f}")
    
    result = {
        'retriever': retriever_name,
        'chunking': chunking_type,
        'precision': precision,
        'recall': recall,
        'entity_recall': entity_recall,
        'latency': total_latency,
        'avg_latency_per_query': total_latency / len(golden_dataset),
        'cost': cost
    }
    
    # Cache the results
    if use_cache:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)
        print(f"  ✓ Cached results to {cache_file}")
    
    return result

