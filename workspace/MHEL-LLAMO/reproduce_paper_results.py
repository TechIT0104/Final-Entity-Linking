import os
import re
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class PaperRun:
	dataset: str  # e.g. HIPE-2020, NewsEye, AJMC, MHERCL
	lang: str
	expected_f1: float
	run_dir: str  # path relative to repo root
	notes: str = ""


def parse_legacy_score_from_result_txt(result_txt: str) -> Optional[float]:
	"""Parse the paper/legacy score from a result.txt.

	- Newer eval.py writes `Precision:` in 0..1, which matches the legacy tp/(tp+fp) metric.
	- Older result.txt files write only `Accuracy:` but that value is actually tp/(tp+fp), often scaled 0..100.
	"""

	m = re.search(r"^Precision\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*$", result_txt, flags=re.MULTILINE)
	if m:
		return float(m.group(1))

	m = re.search(r"^Accuracy\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*$", result_txt, flags=re.MULTILINE)
	if m:
		return float(m.group(1))

	return None


def normalize_accuracy_to_f1(acc_value: float) -> float:
	"""Normalize an Accuracy value to a 0..1 score.

	- Legacy eval.py wrote Accuracy as a percentage (0..100)
	- Updated eval.py may write Accuracy as a fraction (0..1)
	"""

	return acc_value if acc_value <= 1.0 else (acc_value / 100.0)


def read_text(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def fmt_float(x: float, ndigits: int = 3) -> str:
	return f"{x:.{ndigits}f}"


def main() -> None:
	repo_root = os.path.dirname(os.path.abspath(__file__))

	# These are the *best settings* as reported in README.md (mirrors paper table).
	# `run_dir` points to the existing run artifacts folder containing output.csv + result.txt.
	runs: List[PaperRun] = [
		PaperRun("HIPE-2020", "de", 0.620, "results/HIPE_DE/mistral_24B_chain_median_k30_de"),
		PaperRun("HIPE-2020", "en", 0.723, "results/HIPE_EN/mistral_24B_chain_k20_en"),
		PaperRun("HIPE-2020", "fr", 0.692, "results/HIPE_FR/mistral_24B_van_k20_fr"),
		PaperRun("NewsEye", "de", 0.556, "results/NEWSEYE_DE/mistral_24B_chain_k30_de"),
		PaperRun("NewsEye", "fi", 0.509, "results/NEWSEYE_FI/poro2_8B_chain_k20_fi"),
		PaperRun("NewsEye", "fr", 0.662, "results/NEWSEYE_FR/mistral_24B_chain_median_k20_fr"),
		PaperRun("NewsEye", "sv", 0.521, "results/NEWSEYE_SV/gemma_27B_chain_median_k20_sv"),
		PaperRun("AJMC", "de", 0.521, "results/AJMC_DE/mistral_24B_van_k50_de"),
		PaperRun("AJMC", "en", 0.496, "results/AJMC_EN/mistral_24B_van_k50_en"),
		PaperRun("AJMC", "fr", 0.635, "results/AJMC_FR/mistral_24B_van_k20_fr"),
		PaperRun("MHERCL", "en", 0.700, "results/MHERCL_EN/mistral_24B_chain_k20_en"),
		PaperRun("MHERCL", "it", 0.698, "results/MHERCL_IT/mistral_24B_chain_k20_it"),
	]

	rows = []
	ok = 0
	missing = 0
	total = len(runs)

	# The paper table rounds to 3 decimals; use a small tolerance.
	tolerance = 0.01

	for r in runs:
		abs_run_dir = os.path.join(repo_root, r.run_dir)
		result_path = os.path.join(abs_run_dir, "result.txt")
		observed_f1 = None

		if os.path.exists(result_path):
			raw_score = parse_legacy_score_from_result_txt(read_text(result_path))
			if raw_score is not None:
				observed_f1 = normalize_accuracy_to_f1(raw_score)

		if observed_f1 is None:
			status = "MISSING"
			missing += 1
			rows.append((r.dataset, r.lang, r.expected_f1, None, None, status, r.run_dir))
			continue

		delta = observed_f1 - r.expected_f1
		status = "OK" if abs(delta) <= tolerance else "DIFF"
		if status == "OK":
			ok += 1

		rows.append((r.dataset, r.lang, r.expected_f1, observed_f1, delta, status, r.run_dir))

	lines = []
	lines.append("# MHEL-LLaMo — Paper Reproduction Report\n")
	lines.append("This report compares the paper/README best-setting scores against the run artifacts currently in `results/`.\n")
	lines.append(f"- Runs checked: **{total}**\n")
	lines.append(f"- Matched within tolerance (±{tolerance}): **{ok}/{total}**\n")
	if missing:
		lines.append(f"- Missing run folders or result.txt: **{missing}**\n")
	lines.append("\n## Table\n")
	lines.append("| Dataset | Lang | Expected (paper) | Observed (from result.txt) | Δ | Status | Run folder |\n")
	lines.append("|---|---:|---:|---:|---:|---:|---|\n")

	for dataset, lang, expected, observed, delta, status, run_dir in rows:
		if observed is None:
			lines.append(f"| {dataset} | {lang} | {fmt_float(expected)} |  |  | {status} | `{run_dir}` |\n")
		else:
			lines.append(
				"| "
				+ f"{dataset} | {lang} | {fmt_float(expected)} | {fmt_float(observed)} | {fmt_float(delta)} | {status} | `{run_dir}` |\n"
			)

	out_path = os.path.join(repo_root, "reproduction_report.md")
	with open(out_path, "w", encoding="utf-8") as f:
		f.writelines(lines)

	print(f"Wrote {out_path}")
	print(f"OK: {ok}/{total} (missing: {missing})")


if __name__ == "__main__":
	main()