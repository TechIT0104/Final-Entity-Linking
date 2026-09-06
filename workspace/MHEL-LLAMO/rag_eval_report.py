"""
RAG Improvement Evaluation Report.

Compares RAG results against baseline (existing runs)
and generates improvement metrics.
"""

import os
import csv
import json
from typing import Dict, List, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def parse_result_txt(path: str) -> Dict[str, float]:
    """Parse Precision/Accuracy from result.txt."""
    if not os.path.exists(path):
        return {}

    scores = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "Precision:" in line:
                try:
                    val = float(line.split(":")[-1].strip())
                    scores["precision"] = val
                except ValueError:
                    pass
            elif "Accuracy:" in line:
                try:
                    val = float(line.split(":")[-1].strip())
                    scores["accuracy"] = val
                except ValueError:
                    pass
    return scores


def compute_strict_metrics(
    output_csv: str,
    dataset_path: str,
    language: str = "en",
) -> Dict[str, float]:
    """
    Compute strict micro-F1 (correct predictions / gold mentions).

    Args:
        output_csv: Path to output.csv from RAG or baseline
        dataset_path: Path to dataset directory
        language: Language code

    Returns:
        Dict with tp, fp, fn, precision, recall, f1
    """
    # Load gold data
    gold_path = os.path.join(dataset_path, "entities_test.csv")
    if not os.path.exists(gold_path):
        logger.warning(f"Gold data not found: {gold_path}")
        return {}

    gold_map = {}
    with open(gold_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["doc_id"], row["start_pos"])
            gold_map[key] = row.get("gold_label", "NIL")

    # Load predictions
    if not os.path.exists(output_csv):
        logger.warning(f"Output not found: {output_csv}")
        return {}

    tp = 0
    fp = 0
    fn = len(gold_map)

    with open(output_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["doc_id"], row["start_pos"])
            prediction = row.get("prediction", "NIL")

            if key in gold_map:
                fn -= 1
                if prediction == gold_map[key]:
                    tp += 1
                else:
                    fp += 1
            else:
                fp += 1

    # Compute metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def compare_results(
    baseline_csv: str,
    rag_csv: str,
    dataset_path: str,
    dataset_name: str,
    language: str,
) -> Dict[str, any]:
    """
    Compare RAG vs baseline on a dataset.

    Returns:
        Comparison dict with metrics and delta
    """
    logger.info(f"Comparing {dataset_name} ({language})...")

    baseline_metrics = compute_strict_metrics(baseline_csv, dataset_path, language)
    rag_metrics = compute_strict_metrics(rag_csv, dataset_path, language)

    if not baseline_metrics or not rag_metrics:
        logger.warning(f"Could not compute metrics for {dataset_name}")
        return {}

    delta_f1 = rag_metrics["f1"] - baseline_metrics["f1"]
    pct_improvement = (delta_f1 / baseline_metrics["f1"] * 100) if baseline_metrics["f1"] > 0 else 0

    return {
        "dataset": dataset_name,
        "language": language,
        "baseline_f1": baseline_metrics["f1"],
        "baseline_precision": baseline_metrics["precision"],
        "baseline_recall": baseline_metrics["recall"],
        "rag_f1": rag_metrics["f1"],
        "rag_precision": rag_metrics["precision"],
        "rag_recall": rag_metrics["recall"],
        "delta_f1": delta_f1,
        "pct_improvement": pct_improvement,
        "baseline_tp": baseline_metrics["tp"],
        "rag_tp": rag_metrics["tp"],
        "tp_delta": rag_metrics["tp"] - baseline_metrics["tp"],
    }


def generate_report(comparisons: List[Dict]) -> str:
    """Generate HTML report from comparisons."""
    html_head = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RAG Improvement Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    h1 { color: #333; }
    table { border-collapse: collapse; width: 100%; background: white; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background: #0f6b7a; color: white; }
    tr:nth-child(even) { background: #f9f9f9; }
    .positive { color: green; font-weight: bold; }
    .negative { color: red; font-weight: bold; }
    .neutral { color: gray; }
  </style>
</head>
<body>
  <h1>RAG Enhancement Evaluation Report</h1>
  <p>Generated from RAG pipeline runs vs baseline results.</p>
  <table>
    <thead>
      <tr>
        <th>Dataset (Lang)</th>
        <th>Baseline F1</th>
        <th>RAG F1</th>
        <th>ΔF1</th>
        <th>% Improvement</th>
        <th>Baseline TP</th>
        <th>RAG TP</th>
        <th>TP Gain</th>
      </tr>
    </thead>
    <tbody>
"""

    for comp in comparisons:
        delta_class = "positive" if comp["delta_f1"] > 0 else ("negative" if comp["delta_f1"] < 0 else "neutral")
        pct_class = "positive" if comp["pct_improvement"] > 0 else ("negative" if comp["pct_improvement"] < 0 else "neutral")

        html_head += f"""
      <tr>
        <td><strong>{comp["dataset"]} ({comp["language"]})</strong></td>
        <td>{comp["baseline_f1"]:.4f}</td>
        <td>{comp["rag_f1"]:.4f}</td>
        <td class="{delta_class}">{comp["delta_f1"]:+.4f}</td>
        <td class="{pct_class}">{comp["pct_improvement"]:+.2f}%</td>
        <td>{comp["baseline_tp"]}</td>
        <td>{comp["rag_tp"]}</td>
        <td class="{delta_class if comp['tp_delta'] > 0 else 'neutral'}">{comp["tp_delta"]:+d}</td>
      </tr>
"""

    html_head += """
    </tbody>
  </table>
  <h2>Summary</h2>
"""

    avg_f1_delta = sum(c["delta_f1"] for c in comparisons) / len(comparisons) if comparisons else 0
    total_tp_gain = sum(c["tp_delta"] for c in comparisons)

    html_head += f"""
  <p><strong>Average F1 improvement:</strong> <span class="{'positive' if avg_f1_delta > 0 else 'neutral'}">{avg_f1_delta:+.4f}</span></p>
  <p><strong>Total TP gains:</strong> <span class="{'positive' if total_tp_gain > 0 else 'neutral'}">{total_tp_gain:+d} correct predictions</span></p>
</body>
</html>
"""

    return html_head


def main():
    # Configuration: compare these datasets
    comparisons_config = [
        {
            "dataset": "AJMC_EN",
            "language": "en",
            "baseline_folder": "results/AJMC_EN/mistral_24B_van_k50_en",
            "rag_folder": "results/AJMC_EN/rag_mistral_24B_k50_en",
            "dataset_path": "test_data/AJMC_EN",
        },
        {
            "dataset": "NEWSEYE_FI",
            "language": "fi",
            "baseline_folder": "results/NEWSEYE_FI/poro2_8B_chain_k20_fi",
            "rag_folder": "results/NEWSEYE_FI/rag_poro2_8B_k20_fi",
            "dataset_path": "test_data/NEWSEYE_FI",
        },
    ]

    comparisons = []
    for config in comparisons_config:
        baseline_csv = os.path.join(config["baseline_folder"], "output.csv")
        rag_csv = os.path.join(config["rag_folder"], "output.csv")

        comp = compare_results(
            baseline_csv,
            rag_csv,
            config["dataset_path"],
            config["dataset"],
            config["language"],
        )

        if comp:
            comparisons.append(comp)
            print(f"\n{config['dataset']}: {comp['rag_f1']:.4f} (was {comp['baseline_f1']:.4f}, {comp['delta_f1']:+.4f})")

    # Generate report
    if comparisons:
        html_report = generate_report(comparisons)
        output_path = "rag_improvement_report.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_report)
        logger.info(f"Wrote report to {output_path}")
    else:
        logger.warning("No successful comparisons to report")


if __name__ == "__main__":
    main()
