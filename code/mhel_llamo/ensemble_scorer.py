"""
Ensemble Confidence Scoring Module for RAG.

Combines:
- Retrieval score (BELA/FAISS)
- Cross-encoder score
- LLM confidence
Into a single robust decision metric.
"""

from typing import Dict, Any, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class EnsembleScorer:
    """Blend multiple confidence sources for robust decisions."""

    def __init__(
        self,
        retrieval_weight: float = 0.3,
        xencoder_weight: float = 0.4,
        llm_weight: float = 0.3,
    ):
        """
        Args:
            retrieval_weight: Weight for BELA retrieval score
            xencoder_weight: Weight for cross-encoder score
            llm_weight: Weight for LLM confidence
        """
        total = retrieval_weight + xencoder_weight + llm_weight
        self.retrieval_weight = retrieval_weight / total
        self.xencoder_weight = xencoder_weight / total
        self.llm_weight = llm_weight / total

        logger.info(
            f"Ensemble weights: retrieval={self.retrieval_weight:.2f}, "
            f"xencoder={self.xencoder_weight:.2f}, llm={self.llm_weight:.2f}"
        )

    @staticmethod
    def extract_llm_confidence(llm_response: str) -> Tuple[Optional[str], float]:
        """
        Extract the entity label and confidence from LLM response.

        Expected formats:
        - "Napoleon Bonaparte"
        - "NIL"
        - "Napoleon Bonaparte (confidence: 0.85)"
        - "NIL (low confidence)"

        Args:
            llm_response: Raw LLM generation output

        Returns:
            (entity_label_or_nil, confidence_0_to_1)
        """
        response = llm_response.strip()

        # Try to extract confidence score
        confidence_match = re.search(r'\(confidence[:\s]*([0-9.]+)', response, re.IGNORECASE)
        if confidence_match:
            try:
                conf = float(confidence_match.group(1))
                conf = max(0.0, min(1.0, conf))  # Clamp to [0, 1]
            except ValueError:
                conf = 0.5
        else:
            # Heuristic: if "low" or "nil" mentioned, lower confidence
            if "nil" in response.lower() and "nil" != response.lower().strip():
                conf = 0.3
            elif "high" in response.lower():
                conf = 0.8
            else:
                conf = 0.5

        # Extract the entity name (first line if multiline)
        entity = response.split('\n')[0].strip()
        entity = re.sub(r'\(.*\)', '', entity).strip()  # Remove parenthetical

        if entity.lower() == "nil":
            return ("NIL", conf)
        elif entity:
            return (entity, conf)
        else:
            return (None, 0.0)

    @staticmethod
    def normalize_retrieval_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """
        Normalize retrieval score to [0, 1].
        BELA/FAISS scores vary; assume they're already normalized or normalize by rank.
        """
        return max(0.0, min(1.0, score))

    @staticmethod
    def normalize_xencoder_score(score: float) -> float:
        """
        Normalize cross-encoder score to [0, 1].
        Cross-encoders output logits; apply sigmoid.
        """
        import math
        # Sigmoid to [0, 1]
        try:
            normalized = 1.0 / (1.0 + math.exp(-score))
            return normalized
        except OverflowError:
            return 1.0 if score > 0 else 0.0

    def compute_ensemble_score(
        self,
        candidate: Dict[str, Any],
        llm_response: str,
        retrieval_rank: int = 1,  # Rank in BELA retrieval (1 = top)
        total_candidates: int = 50,
    ) -> Dict[str, Any]:
        """
        Compute ensemble confidence score for a candidate.

        Args:
            candidate: Candidate dict with scores
            llm_response: LLM's text response
            retrieval_rank: Rank in original BELA retrieval
            total_candidates: Total candidates retrieved

        Returns:
            Dict with ensemble_score and component scores
        """
        # Component 1: Retrieval score (higher rank = lower score)
        retrieval_score = 1.0 - (retrieval_rank - 1) / max(1, total_candidates)
        retrieval_score = self.normalize_retrieval_score(retrieval_score)

        # Component 2: Cross-encoder score
        xencoder_score = candidate.get("_xencoder_score", 0.5)
        xencoder_score = self.normalize_xencoder_score(xencoder_score)

        # Component 3: LLM confidence
        llm_entity, llm_conf = self.extract_llm_confidence(llm_response)
        llm_score = llm_conf

        # Ensemble
        ensemble_score = (
            self.retrieval_weight * retrieval_score
            + self.xencoder_weight * xencoder_score
            + self.llm_weight * llm_score
        )

        return {
            "ensemble_score": ensemble_score,
            "retrieval_score": retrieval_score,
            "xencoder_score": xencoder_score,
            "llm_confidence": llm_score,
            "llm_entity": llm_entity,
            "weights": {
                "retrieval": self.retrieval_weight,
                "xencoder": self.xencoder_weight,
                "llm": self.llm_weight,
            },
        }

    def make_decision(
        self,
        candidate: Dict[str, Any],
        llm_response: str,
        threshold: float = 0.5,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make final decision based on ensemble score.

        Args:
            candidate: Top candidate
            llm_response: LLM response
            threshold: Ensemble score threshold for accepting candidate
            **kwargs: Additional args for compute_ensemble_score

        Returns:
            Decision dict with entity, score, and reasoning
        """
        scores = self.compute_ensemble_score(candidate, llm_response, **kwargs)
        ensemble_score = scores["ensemble_score"]

        # Decide: accept if ensemble score above threshold, else NIL
        if ensemble_score >= threshold:
            decision = {
                "entity": scores["llm_entity"],
                "ensemble_score": ensemble_score,
                "decision": "ACCEPT",
            }
        else:
            decision = {
                "entity": "NIL",
                "ensemble_score": ensemble_score,
                "decision": "REJECT_LOW_CONFIDENCE",
            }

        decision.update(scores)
        return decision
