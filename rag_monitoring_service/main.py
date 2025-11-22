import os
import sys
import argparse
import json
from config import rag_configs
from evaluate import evaluate_all
from optimization import run_experiments, pick_best

GT = os.path.join(os.path.dirname(__file__), "ground_truth.json")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def cmd_evaluate(args):
    top_k = args.top_k or rag_configs.get("TOP_K", 5)
    summary = evaluate_all(GT, top_k=top_k)
    out = os.path.join(REPORTS_DIR, f"eval_summary_topk{top_k}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out}")
    print(
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
        f"latency={summary['avg_latency_s']:.3f}s"
    )

def cmd_optimize(args):
    embedding_models = args.embedding_models or [rag_configs.get("EMBEDDING_MODEL")]
    top_ks = args.top_ks or [rag_configs.get("TOP_K", 5)]
    out = os.path.join(REPORTS_DIR, "opt_reports.json")
    reports = run_experiments(GT, embedding_models, top_ks, out)
    best = pick_best(reports)
    if best:
        print("BEST:", best["embedding_model"], "top_k", best["top_k"])
    print(f"Wrote {out}")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--top-k", type=int, dest="top_k")
    p_opt = sub.add_parser("optimize")
    p_opt.add_argument("--embedding-models", nargs="+", dest="embedding_models")
    p_opt.add_argument("--top-ks", nargs="+", type=int, dest="top_ks")
    args = parser.parse_args()
    if args.cmd == "evaluate":
        cmd_evaluate(args)
    elif args.cmd == "optimize":
        cmd_optimize(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
