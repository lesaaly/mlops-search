import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.search import SearchEngine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--eval", type=Path, default=Path("data/eval.json"))
    parser.add_argument("--ranking-mode", choices=["normal", "reverse"], default="normal")
    parser.add_argument("--min-mrr", type=float, default=0.85)
    parser.add_argument("--min-recall-at-3", type=float, default=0.90)
    args = parser.parse_args()

    engine = SearchEngine(args.artifact_dir, args.ranking_mode)
    cases = json.loads(args.eval.read_text())
    reciprocal_ranks = []
    recalled = 0
    details = []
    for case in cases:
        ids = [item["id"] for item in engine.search(case["query"], 3)]
        ranks = [ids.index(doc_id) + 1 for doc_id in case["relevant"] if doc_id in ids]
        reciprocal_ranks.append(1 / min(ranks) if ranks else 0.0)
        recalled += int(bool(ranks))
        details.append({"query": case["query"], "top3": ids, "relevant": case["relevant"]})

    report = {
        "ranking_mode": args.ranking_mode,
        "mrr": round(sum(reciprocal_ranks) / len(cases), 4),
        "recall_at_3": round(recalled / len(cases), 4),
        "cases": details,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["mrr"] < args.min_mrr or report["recall_at_3"] < args.min_recall_at_3:
        raise SystemExit("quality gate failed")


if __name__ == "__main__":
    main()
