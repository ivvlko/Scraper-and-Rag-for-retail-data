import os
import time
import json
from config import rag_configs
from evaluate import evaluate_all

def run_experiments(ground_truth_path: str, embedding_models: list, top_ks: list, output_path: str):
    reports = []
    for model in embedding_models:
        os.environ["EMBEDDING_MODEL"] = model
        rag_configs["EMBEDDING_MODEL"] = model
        for k in top_ks:
            t0 = time.perf_counter()
            summary = evaluate_all(ground_truth_path, top_k=k)
            t1 = time.perf_counter()
            summary["embedding_model"] = model
            summary["top_k"] = k
            summary["wall_time_s"] = t1 - t0
            reports.append(summary)
            print(
                f"Done model={model} top_k={k} "
                f"hits ids={summary['avg_hit_ids']:.3f} "
                f"price={summary['avg_hit_price']:.3f} "
                f"link={summary['avg_hit_link']:.3f} "
                f"combined={summary['avg_hit_combined']:.3f} "
                f"mrr ids={summary['avg_mrr_ids']:.3f} "
                f"price={summary['avg_mrr_price']:.3f} "
                f"link={summary['avg_mrr_link']:.3f} "
                f"ndcg ids={summary['avg_ndcg_ids']:.3f} "
                f"price={summary['avg_ndcg_price']:.3f} "
                f"link={summary['avg_ndcg_link']:.3f} "
                f"time={summary['avg_latency_s']:.3f}s"
            )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    return reports

def pick_best(reports):
    reports_sorted = sorted(
        reports,
        key=lambda r: (r["avg_ndcg_ids"], r["avg_hit_ids"], -r["avg_latency_s"]),
        reverse=True
    )
    return reports_sorted[0] if reports_sorted else None
