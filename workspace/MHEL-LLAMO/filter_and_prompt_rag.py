"""
RAG-Enhanced Prompting for Entity Disambiguation.

Pipeline:
1. Load candidates from JSON (BELA retrieval)
2. Rerank with cross-encoder
3. Augment context from dataset
4. Generate LLM response
5. Score with ensemble
6. Output results
"""

import json
import csv
import os
import argparse
from typing import List, Dict, Any, Optional
import logging

import transformers
import torch
from tqdm import tqdm

from rag_reranker import CandidateReranker
from context_augmenter import ContextAugmenter
from ensemble_scorer import EnsembleScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resolve_hf_token(cli_token: str) -> str:
    """Resolve HF token from CLI or env vars."""
    if cli_token:
        return cli_token
    return (
        os.environ.get("HUGGINGFACE_HUB_TOKEN")
        or os.environ.get("HF_TOKEN")
        or os.environ.get("HUGGINGFACE_TOKEN")
        or ""
    )


def resolve_torch_dtype() -> torch.dtype:
    """Resolve torch dtype from environment."""
    dtype_str = os.environ.get("MHEL_TORCH_DTYPE", "bfloat16").strip().lower()
    if dtype_str in {"fp16", "float16", "half"}:
        return torch.float16
    if dtype_str in {"fp32", "float32"}:
        return torch.float32
    return torch.bfloat16


class RAGPipeline:
    """Full RAG pipeline for entity linking."""

    def __init__(
        self,
        model_id: str = "mistralai/Mistral-Small-24B-Instruct-2501",
        xencoder_model: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384",
        device: str = "cuda:0",
        hf_token: Optional[str] = None,
    ):
        """Initialize RAG pipeline with LLM and reranker."""
        self.device = device
        self.hf_token = resolve_hf_token(hf_token or "")

        logger.info("Loading LLM pipeline...")
        max_gpu_mem = os.environ.get("MHEL_MAX_GPU_MEM", "").strip()
        max_cpu_mem = os.environ.get("MHEL_MAX_CPU_MEM", "").strip()
        max_memory = None
        if max_gpu_mem or max_cpu_mem:
            max_memory = {}
            if max_gpu_mem:
                max_memory[0] = max_gpu_mem
            if max_cpu_mem:
                max_memory["cpu"] = max_cpu_mem

        device_map = os.environ.get("MHEL_DEVICE_MAP", "auto").strip().lower()
        if device_map == "none":
            device_map = None
        torch_dtype = resolve_torch_dtype()
        if device_map == "cpu":
            torch_dtype = torch.float32

        offload_folder = os.environ.get("MHEL_OFFLOAD_FOLDER", "offload").strip()
        if not offload_folder:
            offload_folder = "offload"
        if max_cpu_mem and device_map not in (None, "cpu", "cuda"):
            os.makedirs(offload_folder, exist_ok=True)

        model_kwargs = {
            "torch_dtype": torch_dtype,
            "low_cpu_mem_usage": True,
            **({"max_memory": max_memory} if max_memory else {}),
        }
        if max_cpu_mem and device_map not in (None, "cuda"):
            model_kwargs["offload_folder"] = offload_folder
            model_kwargs["offload_state_dict"] = True

        self.llm_pipeline = transformers.pipeline(
            "text-generation",
            model=model_id,
            model_kwargs=model_kwargs,
            device_map=device_map,
            token=self.hf_token or None,
        )

        logger.info("Loading cross-encoder reranker...")
        self.reranker = CandidateReranker(model_name=xencoder_model, device=device)

        logger.info("Initializing ensemble scorer...")
        self.scorer = EnsembleScorer(
            retrieval_weight=0.3,
            xencoder_weight=0.4,
            llm_weight=0.3,
        )

        self.augmenter = ContextAugmenter()

    def process_mention(
        self,
        doc_id: str,
        start_pos: int,
        end_pos: int,
        mention: str,
        paragraph: str,
        candidates: List[Dict[str, Any]],
        n_candidates: int = 20,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Process a single mention through the RAG pipeline.

        Returns:
            Result dict with doc_id, start_pos, end_pos, prediction, scores, etc.
        """
        # Step 1: Rerank candidates
        reranked = self.reranker.rerank(mention, candidates, top_k=n_candidates)

        if not reranked:
            return {
                "doc_id": doc_id,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "mention": mention,
                "prediction": "NIL",
                "ensemble_score": 0.0,
                "reason": "no_candidates",
            }

        # Step 2: Augment context
        mention_context = self.augmenter.extract_mention_context(
            paragraph, start_pos, end_pos, context_window=100
        )

        # Step 3: Build augmented prompt
        prompt = self.augmenter.augment_prompt_context(
            mention, mention_context, reranked, n_candidates=min(10, len(reranked))
        )

        # Step 4: Generate LLM response
        try:
            response = self.llm_pipeline(prompt, max_new_tokens=50, do_sample=False)
            llm_text = response[0]["generated_text"]
            # Extract only the response part (after "**Response:**")
            if "**Response:**" in llm_text:
                llm_text = llm_text.split("**Response:**")[-1].strip()
        except Exception as e:
            logger.warning(f"LLM error for {doc_id}:{start_pos}: {e}")
            return {
                "doc_id": doc_id,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "mention": mention,
                "prediction": "NIL",
                "ensemble_score": 0.0,
                "reason": "llm_error",
            }

        # Step 5: Ensemble scoring
        decision = self.scorer.make_decision(
            candidate=reranked[0],
            llm_response=llm_text,
            threshold=threshold,
            retrieval_rank=1,
            total_candidates=len(candidates),
        )

        return {
            "doc_id": doc_id,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "mention": mention,
            "prediction": decision["entity"],
            "ensemble_score": decision["ensemble_score"],
            "retrieval_score": decision["retrieval_score"],
            "xencoder_score": decision["xencoder_score"],
            "llm_confidence": decision["llm_confidence"],
            "llm_response": llm_text,
            "top_candidate": reranked[0].get("label", "?"),
            "decision": decision["decision"],
        }

    def run(
        self,
        json_f: str,
        dataset_path: str,
        output_dir: str,
        n_candidates: int = 20,
        threshold: float = 0.5,
        resume: bool = False,
    ) -> None:
        """
        Run RAG pipeline on all mentions in a dataset.

        Args:
            json_f: Path to candidates JSON
            dataset_path: Path to dataset (paragraphs_test.csv)
            output_dir: Output directory for results
            n_candidates: Max candidates per mention
            threshold: Ensemble score threshold
            resume: Skip already-processed mentions
        """
        # Load candidates
        with open(json_f, "r", encoding="utf-8") as f:
            retriever_results = json.load(f)

        # Load paragraphs
        paragraphs_path = os.path.join(dataset_path, "paragraphs_test.csv")
        with open(paragraphs_path, "r", encoding="utf-8") as f:
            paragraphs = list(csv.DictReader(f))

        os.makedirs(output_dir, exist_ok=True)

        # Track processed
        output_path = os.path.join(output_dir, "output.csv")
        processed_keys = set()
        if resume and os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_keys.add((row["doc_id"], row["start_pos"]))
            logger.info(f"Resuming: {len(processed_keys)} already processed")

        # Main loop
        results = []
        for mention_data in tqdm(retriever_results, desc="Processing mentions"):
            doc_id = mention_data["doc_id"]
            start_pos = int(mention_data["start_pos"])
            end_pos = int(mention_data["end_pos"])
            mention = mention_data["mention"]
            candidates = mention_data.get("candidates", [])

            # Skip if resume
            if resume and (doc_id, str(start_pos)) in processed_keys:
                continue

            # Find paragraph
            paragraph = None
            for para in paragraphs:
                if para["doc_id"] == doc_id:
                    paragraph = para["paragraph"]
                    break

            if not paragraph:
                logger.warning(f"Paragraph not found for {doc_id}")
                continue

            # Process
            result = self.process_mention(
                doc_id,
                start_pos,
                end_pos,
                mention,
                paragraph,
                candidates,
                n_candidates=n_candidates,
                threshold=threshold,
            )

            results.append(result)

            # Write incrementally (for resume capability)
            if len(results) % 10 == 0 or len(results) == len(retriever_results):
                with open(output_path, "a" if len(results) > 10 else "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=result.keys())
                    if len(results) <= 10 or not os.path.exists(output_path):
                        writer.writeheader()
                    writer.writerows(results[-10:])  # Write last batch
                logger.info(f"Wrote {len(results)} results to {output_path}")

        logger.info(f"Completed: {len(results)} mentions processed")


def main():
    parser = argparse.ArgumentParser(description="RAG-Enhanced Entity Disambiguation")
    parser.add_argument("--json_f", type=str, required=True, help="Path to candidates JSON")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to dataset directory")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory")
    parser.add_argument("--n_candidates", type=int, default=20, help="Max candidates per mention")
    parser.add_argument("--threshold", type=float, default=0.5, help="Ensemble score threshold")
    parser.add_argument("--model_id", type=str, default="mistralai/Mistral-Small-24B-Instruct-2501")
    parser.add_argument("--xencoder_model", type=str, default="cross-encoder/mmarco-mMiniLMv2-L12-H384")
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--hf_token", type=str, default="")
    parser.add_argument("--resume", action="store_true", help="Resume from existing output.csv")

    args = parser.parse_args()

    pipeline = RAGPipeline(
        model_id=args.model_id,
        xencoder_model=args.xencoder_model,
        device=args.device,
        hf_token=args.hf_token,
    )

    pipeline.run(
        json_f=args.json_f,
        dataset_path=args.dataset_path,
        output_dir=args.output_dir,
        n_candidates=args.n_candidates,
        threshold=args.threshold,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
