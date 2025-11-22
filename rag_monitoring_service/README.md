# Monitoring Service

This service combines evaluation and optimization framework. In *main.py* is the command line interface that is going to invoke them. The final results
will be stored in "/reports".

## 1. Evaluation service (logic in *evaluate.py*)

Measures how well the RAG system (embedding + retrieval + GPT answer) performs on a given ground truth dataset (ground_truth.json)

### How to Run:

`docker compose run --rm rag_orchestrator python main.py evaluate --top-k 5`

Check the results to measure faithfulness and relevancy manually. 

### Workflow:
- Takes a ground truth JSON file with queries and expected answers (ids, price, URLs, etc.).

For each query:

- Generates the embedding.

- Queries the database to retrieve top-K items.

- Compares the results with expected answers.

Then computes metrics like:

- Hit rate (was the expected result in top-K)

- MRR (Mean Reciprocal Rank)

- NDCG (Normalized Discounted Cumulative Gain)

- Latency / timings

And returns a summary of all these metrics.

## 2. Optimization/experimentation service (logic in *optimization.py*)

Systematically tune the RAG system by experimenting with different configurations and selecting the best one.

### How to Run

`docker compose run --rm rag_orchestrator python main.py optimize --embedding-models text-embedding-3-small text-embedding-3-large --top-ks 3 5 10`

You can test with different models, system prompts, top_k values etc.

### Workflow:

- Accepts multiple embedding models and top-K values as inputs.

For each combination of embedding model + top-K:

- Calls evaluate_all() (from evaluate.py) to get metrics.

- Records the results along with wall-clock time.

- Aggregates all results into a report (opt_reports.json).

- Picks the best configuration based on metrics (e.g., highest NDCG + hit rate + lowest latency).

It’s like hyperparameter tuning in a sense: shows which embedding model and top-K value gives the best performance on our evaluation dataset

