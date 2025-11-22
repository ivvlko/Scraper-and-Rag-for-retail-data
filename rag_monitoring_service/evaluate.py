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


def evaluate_once(query: str, expected_ids: List[str], top_k: int = 5):
    t0 = time.perf_counter()
    vector = embed(query)
    t1 = time.perf_counter()
    results = query_db(vector, top_k=top_k)
    t2 = time.perf_counter()
    ids = [r['id'] for r in results]
    hit = int(any(e in ids for e in expected_ids)) if expected_ids else 0
    mrr = 0.0

    for rank, rid in enumerate(ids, start=1):
        if rid in expected_ids:
            mrr = 1.0 / rank
            break
    true_relevance = [1 if r in expected_ids else 0 for r in ids]
    if sum(true_relevance) == 0:
        ndcg = 0.0
    else:
        ndcg = ndcg_score([true_relevance], [true_relevance])
    return {
        "query": query,
        "expected": expected_ids,
        "retrieved": ids,
        "hit": hit,
        "mrr": mrr,
        "ndcg": ndcg,
        "embed_time": t1 - t0,
        "db_time": t2 - t1,
        "total_time": t2 - t0
    }


def evaluate_all(ground_truth_path: str, top_k: int = 5):
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
    results = []
    for c in cases:
        q = c.get("query")
        expected = c.get("expected_ids", [])
        res = evaluate_once(q, expected, top_k=top_k)
        results.append(res)
    avg_hit = np.mean([r["hit"] for r in results])
    avg_mrr = np.mean([r["mrr"] for r in results])
    avg_ndcg = np.mean([r["ndcg"] for r in results])
    avg_latency = np.mean([r["total_time"] for r in results])
    summary = {
        "cases": len(results),
        "top_k": top_k,
        "avg_hit": float(avg_hit),
        "avg_mrr": float(avg_mrr),
        "avg_ndcg": float(avg_ndcg),
        "avg_latency_s": float(avg_latency),
        "details": results
    }
    return summary
