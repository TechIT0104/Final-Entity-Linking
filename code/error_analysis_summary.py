"""Summarize FP/FN error profiles from eval.py outputs."""

import argparse
import csv
import os
from collections import Counter
from statistics import mean, median


def _load_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _get_mention(row):
    return (row.get("surface") or row.get("mention") or "").strip()


def _get_type(row):
    return (row.get("type") or "").strip() or "UNKNOWN"


def _get_identifier(row):
    return (row.get("identifier") or "").strip() or "NIL"


def _len_stats(rows):
    lengths = [len(_get_mention(r)) for r in rows if _get_mention(r)]
    if not lengths:
        return None
    return {
        "mean": mean(lengths),
        "median": median(lengths),
        "min": min(lengths),
        "max": max(lengths),
    }


def _top_counts(rows, key_fn, limit=10):
    counts = Counter(key_fn(r) for r in rows if key_fn(r))
    return counts.most_common(limit)


def _read_metrics(path_results):
    metrics_path = os.path.join(path_results, "result.txt")
    if not os.path.exists(metrics_path):
        return {}
    metrics = {}
    with open(metrics_path, "r", encoding="utf-8") as handle:
        for line in handle:
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            metrics[key.strip()] = val.strip()
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Summarize eval.py error outputs")
    parser.add_argument("--path_results", required=True, help="Results folder with fp_ed.csv/fn_ed.csv")
    parser.add_argument(
        "--output",
        default="error_summary.md",
        help="Output markdown file name (written inside path_results)",
    )
    args = parser.parse_args()

    fp_rows = _load_csv(os.path.join(args.path_results, "fp_ed.csv"))
    fn_rows = _load_csv(os.path.join(args.path_results, "fn_ed.csv"))
    tp_rows = _load_csv(os.path.join(args.path_results, "tp_ed.csv"))
    metrics = _read_metrics(args.path_results)

    fp_len = _len_stats(fp_rows)
    fn_len = _len_stats(fn_rows)

    output_path = os.path.join(args.path_results, args.output)

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("# Error Analysis Summary\n\n")
        handle.write(f"Results folder: {args.path_results}\n\n")

        if metrics:
            handle.write("## Metrics (from result.txt)\n")
            for key in ["Precision", "Recall", "F1", "Accuracy"]:
                if key in metrics:
                    handle.write(f"- {key}: {metrics[key]}\n")
            handle.write("\n")

        handle.write("## Counts\n")
        handle.write(f"- True Positives: {len(tp_rows)}\n")
        handle.write(f"- False Positives: {len(fp_rows)}\n")
        handle.write(f"- False Negatives: {len(fn_rows)}\n\n")

        handle.write("## False Positives\n")
        handle.write("Top types:\n")
        for k, v in _top_counts(fp_rows, _get_type):
            handle.write(f"- {k}: {v}\n")
        handle.write("\nTop mentions:\n")
        for k, v in _top_counts(fp_rows, _get_mention):
            handle.write(f"- {k}: {v}\n")

        nil_fp = sum(1 for r in fp_rows if _get_identifier(r) == "NIL")
        handle.write(f"\nNIL predictions in FP: {nil_fp}\n")

        if fp_len:
            handle.write(
                f"Avg mention length in FP: {fp_len['mean']:.2f} "
                f"(median {fp_len['median']:.2f}, min {fp_len['min']}, max {fp_len['max']})\n"
            )

        handle.write("\n## False Negatives\n")
        handle.write("Top types:\n")
        for k, v in _top_counts(fn_rows, _get_type):
            handle.write(f"- {k}: {v}\n")
        handle.write("\nTop mentions:\n")
        for k, v in _top_counts(fn_rows, _get_mention):
            handle.write(f"- {k}: {v}\n")

        if fn_len:
            handle.write(
                f"\nAvg mention length in FN: {fn_len['mean']:.2f} "
                f"(median {fn_len['median']:.2f}, min {fn_len['min']}, max {fn_len['max']})\n"
            )

        handle.write("\n## Notes\n")
        handle.write("- Consider inspecting FP/FN rows with long mentions or NIL-heavy errors.\n")
        handle.write("- Use these counts to justify threshold or reranking changes.\n")

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
