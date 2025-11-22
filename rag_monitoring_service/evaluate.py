import os
import time
import json
from typing import List
import numpy as np
from sklearn.metrics import ndcg_score
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor
from config import rag_configs


PG_URI = os.getenv("PG_URI", "postgresql://postgres:postgres@db:5432/postgres")
EMBEDDING_MODEL = rag_configs.get("EMBEDDING_MODEL")
OPEN_AI_KEY = rag_configs.get("OPEN_AI_API_KEY")

client = OpenAI(api_key=OPEN_AI_KEY)


def embed(text: str):
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return resp.data[0].embedding


def query_db(vector: List[float], top_k: int = 5):
    conn = psycopg2.connect(PG_URI, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, url, text, 1 - (embedding <=> %s::vector) AS score
        FROM fosils_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (vector, vector, top_k)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def evaluate_once(query: str, expected: dict, top_k: int = 5):
    t0 = time.perf_counter()
    vector = embed(query)
    t1 = time.perf_counter()
    results = query_db(vector, top_k=top_k)
    t2 = time.perf_counter()

    ids = [r.get("id") for r in results]
    prices = [str(r.get("price")) for r in results]
    links = [r.get("url") for r in results]

    expected_ids = expected.get("expected_ids", [])
    expected_price = expected.get("expected_price", [])
    expected_link = expected.get("expected_link", [])

    def compute_metrics(retrieved, expected_values):
        if not expected_values:
            return {"hit": 0, "mrr": 0.0, "ndcg": 0.0}
        hit = int(any(v in retrieved for v in expected_values))
        mrr = 0.0
        for rank, item in enumerate(retrieved, start=1):
            if item in expected_values:
                mrr = 1.0 / rank
                break
        true_rel = [1 if r in expected_values else 0 for r in retrieved]
        ndcg = ndcg_score([true_rel], [true_rel]) if sum(true_rel) > 0 else 0.0
        return {"hit": hit, "mrr": mrr, "ndcg": ndcg}

    metrics_ids = compute_metrics(ids, expected_ids)
    metrics_price = compute_metrics(prices, expected_price)
    metrics_link = compute_metrics(links, expected_link)

    all_hits = [metrics_ids["hit"], metrics_price["hit"], metrics_link["hit"]]
    combined_hit = max(all_hits)

    return {
        "query": query,
        "expected": expected,
        "retrieved_ids": ids,
        "retrieved_prices": prices,
        "retrieved_links": links,
        "metrics_ids": metrics_ids,
        "metrics_price": metrics_price,
        "metrics_link": metrics_link,
        "combined_hit": combined_hit,
        "embed_time": t1 - t0,
        "db_time": t2 - t1,
        "total_time": t2 - t0
    }


def evaluate_all(ground_truth_path: str, top_k: int = 5):
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    results = []
    for c in cases:
        query = c.get("query")
        expected = {
            "expected_ids": c.get("expected_ids", []),
            "expected_price": c.get("expected_price", []),
            "expected_link": c.get("expected_link", [])
        }
        res = evaluate_once(query, expected, top_k=top_k)
        results.append(res)

    avg_hit_ids = float(np.mean([r["metrics_ids"]["hit"] for r in results]))
    avg_hit_price = float(np.mean([r["metrics_price"]["hit"] for r in results]))
    avg_hit_link = float(np.mean([r["metrics_link"]["hit"] for r in results]))
    avg_hit_combined = float(np.mean([r["combined_hit"] for r in results]))

    avg_mrr_ids = float(np.mean([r["metrics_ids"]["mrr"] for r in results]))
    avg_mrr_price = float(np.mean([r["metrics_price"]["mrr"] for r in results]))
    avg_mrr_link = float(np.mean([r["metrics_link"]["mrr"] for r in results]))

    avg_ndcg_ids = float(np.mean([r["metrics_ids"]["ndcg"] for r in results]))
    avg_ndcg_price = float(np.mean([r["metrics_price"]["ndcg"] for r in results]))
    avg_ndcg_link = float(np.mean([r["metrics_link"]["ndcg"] for r in results]))

    avg_latency = float(np.mean([r["total_time"] for r in results]))

    summary = {
        "cases": len(results),
        "top_k": top_k,
        "avg_hit_ids": avg_hit_ids,
        "avg_hit_price": avg_hit_price,
        "avg_hit_link": avg_hit_link,
        "avg_hit_combined": avg_hit_combined,
        "avg_mrr_ids": avg_mrr_ids,
        "avg_mrr_price": avg_mrr_price,
        "avg_mrr_link": avg_mrr_link,
        "avg_ndcg_ids": avg_ndcg_ids,
        "avg_ndcg_price": avg_ndcg_price,
        "avg_ndcg_link": avg_ndcg_link,
        "avg_latency_s": avg_latency,
        "details": results
    }

    return summary