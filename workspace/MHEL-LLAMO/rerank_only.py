"""Cross-encoder rerank baseline (CPU-friendly).

Reads BELA candidate JSON and reranks candidates with a cross-encoder,
then writes output.csv compatible with eval.py.
"""

import argparse
import csv
import json
import os
from typing import Dict, List, Optional

from sentence_transformers import CrossEncoder
from tqdm import tqdm


def _get_mention(item: Dict) -> str:
    return (item.get("mention") or item.get("surface") or "").strip()


def _get_candidate_text(cand: Dict) -> str:
    label = (cand.get("label") or "").strip()
    descr = (cand.get("descr") or "").strip()
    if label and descr:
        return f"{label}. {descr}"
    if label:
        return label
    if descr:
        return descr
    return (cand.get("wb_id") or "").strip()


def _build_context(paragraph: str, start_pos: int, end_pos: int, window: int) -> str:
    if not paragraph:
        return ""
    start = max(0, start_pos - window)
    end = min(len(paragraph), end_pos + window)
    return paragraph[start:end]


def _load_paragraphs(dataset_path: Optional[str]) -> Dict[str, str]:
    if not dataset_path:
        return {}
    paragraphs_path = os.path.join(dataset_path, "paragraphs_test.csv")
    if not os.path.exists(paragraphs_path):
        return {}

    paragraphs = {}
    with open(paragraphs_path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            doc_id = (row.get("doc_id") or "").strip()
            if not doc_id:
                continue
            paragraphs[doc_id] = row.get("paragraph", "")
    return paragraphs


def rerank_candidates(
    data: List[Dict],
    paragraphs: Dict[str, str],
    model_name: str,
    output_path: str,
    top_k: int,
    batch_size: int,
    use_context: bool,
    context_window: int,
) -> None:
    model = CrossEncoder(model_name, device="cpu")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "doc_id",
            "start_pos",
            "end_pos",
            "surface",
            "gt_id",
            "type",
            "identifier",
            "title",
            "answer",
            "score",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for item in tqdm(data, desc="Reranking"):
            doc_id = (item.get("doc_id") or "").strip()
            start_pos_raw = item.get("start_pos", "")
            end_pos_raw = item.get("end_pos", "")
            mention = _get_mention(item)
            if not mention:
                continue

            candidates = item.get("candidates") or []
            if top_k and len(candidates) > top_k:
                candidates = candidates[:top_k]

            paragraph = paragraphs.get(doc_id, "")
            try:
                start_pos = int(float(start_pos_raw))
                end_pos = int(float(end_pos_raw))
            except Exception:
                start_pos = start_pos_raw
                end_pos = end_pos_raw

            if use_context and paragraph and isinstance(start_pos, int) and isinstance(end_pos, int):
                context = _build_context(paragraph, start_pos, end_pos, context_window)
            else:
                context = mention

            if not candidates:
                writer.writerow(
                    {
                        "doc_id": doc_id,
                        "start_pos": start_pos_raw,
                        "end_pos": end_pos_raw,
                        "surface": mention,
                        "gt_id": item.get("identifier", ""),
                        "type": item.get("type", ""),
                        "identifier": "NIL",
                        "title": "",
                        "answer": "no_candidates",
                        "score": 0.0,
                    }
                )
                continue

            pairs = []
            for cand in candidates:
                cand_text = _get_candidate_text(cand)
                pairs.append([context, cand_text])

            scores = model.predict(pairs, batch_size=batch_size)
            best_idx = max(range(len(scores)), key=lambda i: scores[i])
            best_cand = candidates[best_idx]

            writer.writerow(
                {
                    "doc_id": doc_id,
                    "start_pos": start_pos_raw,
                    "end_pos": end_pos_raw,
                    "surface": mention,
                    "gt_id": item.get("identifier", ""),
                    "type": item.get("type", ""),
                    "identifier": best_cand.get("wb_id", "NIL") or "NIL",
                    "title": best_cand.get("label", ""),
                    "answer": "cross_encoder_rerank",
                    "score": float(scores[best_idx]),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-encoder rerank baseline")
    parser.add_argument("--json_f", required=True, help="Path to candidates JSON")
    parser.add_argument("--dataset_path", default="", help="Path to dataset directory")
    parser.add_argument("--output_dir", required=True, help="Output directory")
    parser.add_argument(
        "--xencoder_model",
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        help="Cross-encoder model ID",
    )
    parser.add_argument("--top_k", type=int, default=20, help="Max candidates to rerank")
    parser.add_argument("--batch_size", type=int, default=16, help="Cross-encoder batch size")
    parser.add_argument("--context_window", type=int, default=100, help="Context window size")
    parser.add_argument("--no_context", action="store_true", help="Disable paragraph context")
    parser.add_argument("--max_mentions", type=int, default=0, help="Limit number of mentions")
    args = parser.parse_args()

    with open(args.json_f, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    if args.max_mentions and len(data) > args.max_mentions:
        data = data[: args.max_mentions]

    paragraphs = _load_paragraphs(args.dataset_path)

    output_path = os.path.join(args.output_dir, "output.csv")
    rerank_candidates(
        data=data,
        paragraphs=paragraphs,
        model_name=args.xencoder_model,
        output_path=output_path,
        top_k=args.top_k,
        batch_size=args.batch_size,
        use_context=not args.no_context,
        context_window=args.context_window,
    )

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
