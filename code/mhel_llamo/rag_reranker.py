"""
Cross-Encoder Reranking Module for RAG.

Uses a cross-encoder to rerank BELA-retrieved candidates,
improving relevance without additional LLM calls.
"""

import torch
from typing import List, Dict, Any, Tuple
from sentence_transformers import CrossEncoder
import logging

logger = logging.getLogger(__name__)


class CandidateReranker:
    """Rerank candidates using a cross-encoder model."""

    def __init__(self, model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384", device: str = "cuda:0"):
        """
        Args:
            model_name: HF model ID for cross-encoder
            device: torch device (cuda:0 or cpu)
        """
        self.device = device
        self.model = CrossEncoder(model_name, device=device)
        logger.info(f"Loaded cross-encoder: {model_name} on {device}")

    def rerank(
        self,
        mention: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidates by cross-encoder relevance score.

        Args:
            mention: The mention text (e.g., "Napoleon Bonaparte")
            candidates: List of candidate dicts (must have "label" key)
            top_k: Return only top-k candidates

        Returns:
            Reranked candidates, sorted by score descending, with "_xencoder_score" added.
        """
        if not candidates:
            return []

        # Prepare inputs: pairs of (mention, candidate_label)
        pairs = [
            [mention, cand.get("label", "")] for cand in candidates
        ]

        # Score all pairs
        with torch.no_grad():
            scores = self.model.predict(pairs)

        # Attach scores and sort
        for cand, score in zip(candidates, scores):
            cand["_xencoder_score"] = float(score)

        # Sort by cross-encoder score descending
        reranked = sorted(candidates, key=lambda x: x["_xencoder_score"], reverse=True)

        return reranked[:top_k]

    def rerank_batch(
        self,
        mentions: List[str],
        candidate_lists: List[List[Dict[str, Any]]],
        top_k: int = 20,
    ) -> List[List[Dict[str, Any]]]:
        """
        Batch reranking for efficiency.

        Args:
            mentions: List of mention texts
            candidate_lists: List of candidate lists (one per mention)
            top_k: Return only top-k per list

        Returns:
            List of reranked candidate lists
        """
        results = []
        for mention, candidates in zip(mentions, candidate_lists):
            results.append(self.rerank(mention, candidates, top_k))
        return results
