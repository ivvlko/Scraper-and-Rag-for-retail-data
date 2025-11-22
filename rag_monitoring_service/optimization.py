import os
import json
import time
from evaluate import evaluate_all, embed, query_db
from config import rag_configs


def run_experiments(ground_truth_path: str, embedding_models: list, top_ks: list, output_path: str):
    reports = []
    baseline = {}
    for model in embedding_models:
        os.environ["EMBEDDING_MODEL"] = model
        rag_configs["EMBEDDING_MODEL"] = model
        for k in top_ks:
            t0 = time.perf_counter()
            summary = evaluate_all(ground_truth_path, top_k=k)
            t1 = time.perf_counter()
            summary["embedding_model"] = model
            summary["wall_time_s"] = t1 - t0
            reports.append(summary)
            print(f"Done model={model} top_k={k} hit={summary['avg_hit']:.3f} mrr={summary['avg_mrr']:.3f} ndcg={summary['avg_ndcg']:.3f} time={summary['avg_latency_s']:.3f}s")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    return reports

def pick_best(reports):
    reports_sorted = sorted(reports, key=lambda r: (r["avg_ndcg"], r["avg_hit"], -r["avg_latency_s"]), reverse=True)
    return reports_sorted[0] if reports_sorted else None
