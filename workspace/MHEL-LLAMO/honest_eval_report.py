import csv
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class BestRun:
	dataset_key: str  # matches test_data folder, e.g. HIPE_EN, NEWSEYE_FR, AJMC_DE, MHERCL_it
	lang: str
	paper_expected: float
	run_dir: str  # relative path to run folder containing output.csv


def _norm_id(raw_id: str) -> str:
	raw_id = (raw_id or "").strip().upper()
	return raw_id if raw_id.startswith("Q") else "NIL"


def _norm_pos(raw_pos) -> str:
	s = str(raw_pos).strip() if raw_pos is not None else ""
	if s == "":
		return ""
	try:
		return str(int(float(s)))
	except Exception:
		return s


def read_csv_rows(path: str) -> List[Dict[str, str]]:
	with open(path, "r", encoding="utf-8") as f:
		return list(csv.DictReader(f))


def evaluate_strict(gold_rows: List[Dict[str, str]], pred_rows: List[Dict[str, str]]) -> Dict[str, float]:
	"""Strict micro evaluation over all gold mentions (doc_id + start_pos join).

	Assumes there should be one prediction per gold mention.
	- strict_accuracy == strict_micro_f1 in this setting
	"""

	gold_by_key = {(r.get("doc_id"), _norm_pos(r.get("start_pos"))): _norm_id(r.get("identifier", "")) for r in gold_rows}
	pred_by_key = {(r.get("doc_id"), _norm_pos(r.get("start_pos"))): _norm_id(r.get("identifier", "")) for r in pred_rows}

	total = len(gold_by_key)
	pred_rows_n = len(pred_rows)
	pred_unique_n = len(pred_by_key)
	matched = 0
	correct = 0

	for key, gold_id in gold_by_key.items():
		if key in pred_by_key:
			matched += 1
			if pred_by_key[key] == gold_id:
				correct += 1

	missing_gold = total - matched
	extra_pred = sum(1 for k in pred_by_key.keys() if k not in gold_by_key)

	coverage = matched / total if total else 0.0
	strict_accuracy = correct / total if total else 0.0

	# In a one-prediction-per-gold setup: micro P=R=F1=accuracy
	strict_precision = correct / matched if matched else 0.0
	strict_recall = strict_accuracy
	strict_f1 = (2 * strict_precision * strict_recall / (strict_precision + strict_recall)) if (strict_precision + strict_recall) else 0.0

	return {
		"strict_total": float(total),
		"strict_matched": float(matched),
		"pred_rows": float(pred_rows_n),
		"pred_unique": float(pred_unique_n),
		"missing_gold": float(missing_gold),
		"extra_pred": float(extra_pred),
		"coverage": coverage,
		"strict_accuracy": strict_accuracy,
		"strict_precision": strict_precision,
		"strict_recall": strict_recall,
		"strict_f1": strict_f1,
	}


def evaluate_paper_legacy(gold_rows: List[Dict[str, str]], pred_rows: List[Dict[str, str]]) -> Dict[str, float]:
	"""Recreate the repo/paper legacy score used in the published table.

	The historical eval script effectively scored tp/(tp+fp) over joined rows
	(i.e., precision over the subset of gold mentions that have a prediction).
	"""

	gold_by_key = {(r.get("doc_id"), _norm_pos(r.get("start_pos"))): _norm_id(r.get("identifier", "")) for r in gold_rows}
	pred_by_key = {(r.get("doc_id"), _norm_pos(r.get("start_pos"))): _norm_id(r.get("identifier", "")) for r in pred_rows}

	tp = 0
	fp = 0
	joined = 0
	for key, gold_id in gold_by_key.items():
		if key in pred_by_key:
			joined += 1
			if pred_by_key[key] == gold_id:
				tp += 1
			else:
				fp += 1

	paper_score = tp / (tp + fp) if (tp + fp) else 0.0
	return {
		"paper_tp": float(tp),
		"paper_fp": float(fp),
		"paper_joined": float(joined),
		"paper_score": paper_score,
	}


def fmt(x: Optional[float], nd: int = 3) -> str:
	if x is None:
		return ""
	return f"{x:.{nd}f}"


def infer_test_data_dir(dataset_key_from_results: str) -> str:
	"""Map results folder keys to test_data folder keys."""

	# Most match exactly, except MHERCL_IT results folder vs MHERCL_it test_data.
	if dataset_key_from_results.upper() == "MHERCL_IT":
		return "MHERCL_it"
	return dataset_key_from_results


def iter_result_run_dirs(repo_root: str) -> Iterable[str]:
	results_root = os.path.join(repo_root, "results")
	if not os.path.isdir(results_root):
		return
	for dataset_dirname in sorted(os.listdir(results_root)):
		dataset_abs = os.path.join(results_root, dataset_dirname)
		if not os.path.isdir(dataset_abs):
			continue
		for run_dirname in sorted(os.listdir(dataset_abs)):
			run_abs = os.path.join(dataset_abs, run_dirname)
			if not os.path.isdir(run_abs):
				continue
			if os.path.exists(os.path.join(run_abs, "output.csv")):
				yield os.path.relpath(run_abs, repo_root)


def main() -> None:
	repo_root = os.path.dirname(os.path.abspath(__file__))

	runs: List[BestRun] = [
		BestRun("HIPE_DE", "de", 0.620, "results/HIPE_DE/mistral_24B_chain_median_k30_de"),
		BestRun("HIPE_EN", "en", 0.723, "results/HIPE_EN/mistral_24B_chain_k20_en"),
		BestRun("HIPE_FR", "fr", 0.692, "results/HIPE_FR/mistral_24B_van_k20_fr"),
		BestRun("NEWSEYE_DE", "de", 0.556, "results/NEWSEYE_DE/mistral_24B_chain_k30_de"),
		BestRun("NEWSEYE_FI", "fi", 0.509, "results/NEWSEYE_FI/poro2_8B_chain_k20_fi"),
		BestRun("NEWSEYE_FR", "fr", 0.662, "results/NEWSEYE_FR/mistral_24B_chain_median_k20_fr"),
		BestRun("NEWSEYE_SV", "sv", 0.521, "results/NEWSEYE_SV/gemma_27B_chain_median_k20_sv"),
		BestRun("AJMC_DE", "de", 0.521, "results/AJMC_DE/mistral_24B_van_k50_de"),
		BestRun("AJMC_EN", "en", 0.496, "results/AJMC_EN/mistral_24B_van_k50_en"),
		BestRun("AJMC_FR", "fr", 0.635, "results/AJMC_FR/mistral_24B_van_k20_fr"),
		BestRun("MHERCL_EN", "en", 0.700, "results/MHERCL_EN/mistral_24B_chain_k20_en"),
		BestRun("MHERCL_IT", "it", 0.698, "results/MHERCL_IT/mistral_24B_chain_k20_it"),
	]

	lines: List[str] = []
	lines.append("# Honest Paper Evaluation (Best Settings)\n")
	lines.append("This report evaluates the *existing* run artifacts under `results/` for the paper’s reported best settings.\n")
	lines.append("\n## Metrics\n")
	lines.append("- **Paper/legacy score**: matches the repo’s original scoring used for the published table (tp/(tp+fp) on joined rows).\n")
	lines.append("- **Strict micro-F1/accuracy**: correct predictions / total gold mentions (doc_id+start_pos join).\n")
	lines.append("\n## Table\n")
	lines.append("| Dataset | Lang | Paper expected | Paper score | Δ | Strict F1 | Coverage | Gold N | Pred uniq | Pred rows | Missing gold | Extra pred | Run folder |\n")
	lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")

	ok_paper = 0
	ok_strict = 0
	tol = 0.01

	for r in runs:
		run_abs = os.path.join(repo_root, r.run_dir)
		output_csv = os.path.join(run_abs, "output.csv")
		if not os.path.exists(output_csv):
			lines.append(f"| {r.dataset_key} | {r.lang} | {fmt(r.paper_expected)} |  |  |  |  |  |  |  |  |  | `{r.run_dir}` (missing output.csv) |\n")
			continue

		test_dir = os.path.join(repo_root, "test_data", infer_test_data_dir(r.dataset_key))
		gold_csv = os.path.join(test_dir, "annotations_test.csv")
		if not os.path.exists(gold_csv):
			lines.append(f"| {r.dataset_key} | {r.lang} | {fmt(r.paper_expected)} |  |  |  |  |  |  |  |  |  | `{r.run_dir}` (missing gold) |\n")
			continue

		gold = read_csv_rows(gold_csv)
		preds = read_csv_rows(output_csv)

		paper = evaluate_paper_legacy(gold, preds)
		strict = evaluate_strict(gold, preds)

		paper_score = paper["paper_score"]
		strict_f1 = strict["strict_f1"]
		coverage = strict["coverage"]
		gold_n = int(strict["strict_total"])
		pred_unique = int(strict["pred_unique"])
		pred_rows_n = int(strict["pred_rows"])
		missing_gold = int(strict["missing_gold"])
		extra_pred = int(strict["extra_pred"])
		delta = paper_score - r.paper_expected

		if abs(paper_score - r.paper_expected) <= tol:
			ok_paper += 1
		# strict has no paper-expected target; but we track completeness (coverage ~ 1)
		if coverage >= 0.999:
			ok_strict += 1

		lines.append(
			f"| {r.dataset_key} | {r.lang} | {fmt(r.paper_expected)} | {fmt(paper_score)} | {fmt(delta)} | {fmt(strict_f1)} | {fmt(coverage)} | {gold_n} | {pred_unique} | {pred_rows_n} | {missing_gold} | {extra_pred} | `{r.run_dir}` |\n"
		)

	lines.append("\n## Summary\n")
	lines.append(f"- Paper-score matched (±{tol}): **{ok_paper}/{len(runs)}**\n")
	lines.append(f"- Strict coverage ~1.0: **{ok_strict}/{len(runs)}**\n")

	out_path = os.path.join(repo_root, "honest_comparison_table.md")
	with open(out_path, "w", encoding="utf-8") as f:
		f.writelines(lines)

	print(f"Wrote {out_path}")

	# Also generate a broad scan over *all* run folders with output.csv
	all_lines: List[str] = []
	all_lines.append("# Honest Evaluation (All Runs Found)\n")
	all_lines.append("This table scans `results/*/*/output.csv` and computes both legacy and strict metrics.\n")
	all_lines.append("\n| Dataset | Run | Paper score | Strict F1 | Coverage | Gold N | Pred uniq | Pred rows | Missing gold | Extra pred | Folder |\n")
	all_lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")

	for run_rel in iter_result_run_dirs(repo_root):
		# run_rel: results/DATASET/RUN
		parts = run_rel.split(os.sep)
		dataset_key = parts[1] if len(parts) >= 3 else ""
		run_name = parts[2] if len(parts) >= 3 else run_rel

		test_dir = os.path.join(repo_root, "test_data", infer_test_data_dir(dataset_key))
		gold_csv = os.path.join(test_dir, "annotations_test.csv")
		output_csv = os.path.join(repo_root, run_rel, "output.csv")

		if not os.path.exists(gold_csv):
			all_lines.append(f"| {dataset_key} | {run_name} |  |  |  |  |  | `{run_rel}` (missing gold) |\n")
			continue

		gold = read_csv_rows(gold_csv)
		preds = read_csv_rows(output_csv)

		paper = evaluate_paper_legacy(gold, preds)
		strict = evaluate_strict(gold, preds)

		paper_score = paper["paper_score"]
		strict_f1 = strict["strict_f1"]
		coverage = strict["coverage"]
		gold_n = int(strict["strict_total"])
		pred_unique = int(strict["pred_unique"])
		pred_rows_n = int(strict["pred_rows"])
		missing_gold = int(strict["missing_gold"])
		extra_pred = int(strict["extra_pred"])
		all_lines.append(
			f"| {dataset_key} | {run_name} | {fmt(paper_score)} | {fmt(strict_f1)} | {fmt(coverage)} | {gold_n} | {pred_unique} | {pred_rows_n} | {missing_gold} | {extra_pred} | `{run_rel}` |\n"
		)

	all_out_path = os.path.join(repo_root, "honest_all_runs_table.md")
	with open(all_out_path, "w", encoding="utf-8") as f:
		f.writelines(all_lines)
	print(f"Wrote {all_out_path}")


if __name__ == "__main__":
	main()

