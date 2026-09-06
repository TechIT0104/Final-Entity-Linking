"""
Context Augmentation Module for RAG.

Enriches entity disambiguation prompts with:
- Mention context (surrounding text)
- Entity metadata (type, dates, related entities)
- Visual structure (better formatting)
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ContextAugmenter:
    """Augment prompts with rich context."""

    @staticmethod
    def extract_mention_context(
        paragraph: str,
        start_pos: int,
        end_pos: int,
        context_window: int = 100,
    ) -> str:
        """
        Extract mention context (surrounding text).

        Args:
            paragraph: Full paragraph text
            start_pos: Mention start position in paragraph
            end_pos: Mention end position
            context_window: Characters before/after to include

        Returns:
            Context snippet with mention highlighted
        """
        ctx_start = max(0, start_pos - context_window)
        ctx_end = min(len(paragraph), end_pos + context_window)

        before = paragraph[ctx_start:start_pos]
        mention = paragraph[start_pos:end_pos]
        after = paragraph[end_pos:ctx_end]

        # Highlight mention with markers
        return f"{before}[***{mention}***]{after}"

    @staticmethod
    def format_candidate(
        candidate: Dict[str, Any],
        rank: int,
    ) -> str:
        """
        Format a single candidate for display in prompt.

        Args:
            candidate: Candidate dict with label, description, type, dates, etc.
            rank: Rank number (1-indexed)

        Returns:
            Formatted candidate string
        """
        label = candidate.get("label", "?")
        descr = candidate.get("descr", "No description")
        entity_type = candidate.get("type", "Unknown")
        date_info = candidate.get("date", "")
        wb_id = candidate.get("wikidata_id", candidate.get("wb_id", ""))

        # Cross-encoder score if available
        xscore = candidate.get("_xencoder_score", None)
        xscore_str = f" [relevance:{xscore:.2f}]" if xscore is not None else ""

        lines = [
            f"  {rank}. **{label}**{xscore_str}",
            f"     Type: {entity_type}",
            f"     Description: {descr}",
        ]

        if date_info:
            lines.append(f"     Date: {date_info}")
        if wb_id:
            lines.append(f"     ID: {wb_id}")

        return "\n".join(lines)

    @staticmethod
    def augment_prompt_context(
        mention: str,
        mention_context: str,
        candidates: List[Dict[str, Any]],
        n_candidates: int = 20,
    ) -> str:
        """
        Build augmented prompt with rich context.

        Args:
            mention: The mention text
            mention_context: Surrounding text from paragraph
            candidates: List of ranked candidates
            n_candidates: How many to show

        Returns:
            Formatted prompt string
        """
        candidates_str = "\n".join(
            ContextAugmenter.format_candidate(c, i + 1)
            for i, c in enumerate(candidates[:n_candidates])
        )

        prompt = f"""You are an entity linking expert for historical text.

**Mention:** {mention}

**Context in document:**
{mention_context}

**Candidate entities (ranked by relevance):**
{candidates_str}

**Task:** Select the most relevant entity for the mention, or select NIL if none match.

**Answer format:**
- If you select an entity, respond with the LABEL exactly as shown.
- If none match, respond with: NIL

**Response:**"""

        return prompt

    @staticmethod
    def augment_prompts_batch(
        mentions: List[str],
        contexts: List[str],
        candidate_lists: List[List[Dict[str, Any]]],
        n_candidates: int = 20,
    ) -> List[str]:
        """
        Batch augment prompts.

        Args:
            mentions: List of mentions
            contexts: List of mention contexts
            candidate_lists: List of candidate lists
            n_candidates: Max candidates per prompt

        Returns:
            List of augmented prompts
        """
        prompts = []
        for mention, context, candidates in zip(mentions, contexts, candidate_lists):
            prompt = ContextAugmenter.augment_prompt_context(
                mention, context, candidates, n_candidates
            )
            prompts.append(prompt)
        return prompts
