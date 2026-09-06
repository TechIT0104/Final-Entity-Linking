import torch
import faiss
import hydra
from hydra.experimental import compose, initialize_config_module
from typing import List, Dict, Any, Tuple, Optional
import logging
import sqlite3
import re
from huggingface_hub import hf_hub_download
import os

logger = logging.getLogger(__name__)


def resolve_hf_token(cli_token: Optional[str] = None) -> Optional[str]:
    if cli_token:
        return cli_token
    return (
        os.environ.get("HUGGINGFACE_HUB_TOKEN")
        or os.environ.get("HF_TOKEN")
        or os.environ.get("HUGGINGFACE_TOKEN")
    )


class EntityDisambiguator:
    """Clean, functional entity disambiguation model using BELA."""

    def __init__(
            self,
            checkpoint_path: Optional[str] = None,
            faiss_index_path: Optional[str] = None,
            wikidata_index_path: Optional[str] = None,
            db_path: Optional[str] = None,
            embedding_dim: int = 300,
            config_name: str = "joint_el_mel",
            device: str = "cuda:0",
            # Hugging Face parameters
            hf_model_name: Optional[str] = None,
            cache_dir: Optional[str] = None
                ,
                hf_token: Optional[str] = None
    ):
        """
        Initialize the entity disambiguation model.

        Args:
            checkpoint_path: Path to the trained model checkpoint
            faiss_index_path: Path to the precomputed FAISS index
            wikidata_index_path: Path to the Wikidata QID index file
            db_path: Path to the SQLITE database containing entity information
            embedding_dim: Embedding dimension
            config_name: Hydra config name for the model
            device: Device to run the model on
            hf_model_name: Hugging Face model name (e.g., "sntcristian/WikiBELA")
            cache_dir: Cache directory for downloaded files
        """

        self.device = torch.device(device)
        self.embedding_dim = embedding_dim

        self.hf_token = resolve_hf_token(hf_token)

        # Load from Hugging Face if model name provided
        if hf_model_name:
            self._load_from_hf(hf_model_name, cache_dir)
        else:
            # Use provided paths or defaults
            self.checkpoint_path = checkpoint_path or "./models/model_wiki.ckpt"
            self.faiss_index_path = faiss_index_path or "./models/faiss.index"
            self.wikidata_index_path = wikidata_index_path or "./models/index.txt"
            self.db_path = db_path or "./models/knowledge_base.sqlite"

        # Load model and components
        self._load_model(config_name)
        self._load_faiss_index()
        self._load_entity_db()

        logger.info(f"EntityDisambiguator initialized")

    def _load_from_hf(self, model_name: str, cache_dir: Optional[str]) -> None:
        """Load model files from Hugging Face Hub."""
        
        files = {
            'checkpoint_path': 'model_wiki.ckpt',
            'faiss_index_path': 'faiss.index',
            'wikidata_index_path': 'index.txt',
            'db_path': 'knowledge_base.sqlite'
        }
        
        for attr, filename in files.items():
            setattr(self, attr, hf_hub_download(
                repo_id=model_name,
                filename=filename,
                cache_dir=cache_dir,
                token=self.hf_token,
            ))

    def _load_model(self, config_name: str) -> None:
        """Load the BELA model from checkpoint."""
        logger.info("Loading BELA model...")

        with initialize_config_module("bela/conf"):
            cfg = compose(config_name=config_name)
            cfg.task.load_from_checkpoint = self.checkpoint_path
            cfg.task.embedding_dim = self.embedding_dim
            cfg.datamodule.ent_catalogue_idx_path = self.wikidata_index_path
            cfg.datamodule.train_path = None
            cfg.datamodule.val_path = None
            cfg.datamodule.test_path = None

        # Initialize components
        self.transform = hydra.utils.instantiate(cfg.task.transform)
        datamodule = hydra.utils.instantiate(cfg.datamodule, transform=self.transform)
        self.task = hydra.utils.instantiate(cfg.task, datamodule=datamodule, _recursive_=False)

        # Setup and move to device
        self.task.setup("train")
        self.task.eval()
        self.task.to(self.device)

    def _load_faiss_index(self) -> None:
        """Load the precomputed FAISS index."""
        logger.info(f"Loading FAISS index from {self.faiss_index_path}")
        self.faiss_index = faiss.read_index(self.faiss_index_path)

        # Move to GPU if available
        try:
            has_gpu_faiss = hasattr(faiss, "StandardGpuResources") and hasattr(faiss, "index_cpu_to_gpu")
            get_num_gpus = getattr(faiss, "get_num_gpus", None)
            num_gpus = int(get_num_gpus()) if callable(get_num_gpus) else 0

            if self.device.type == "cuda" and has_gpu_faiss and num_gpus > 0:
                res = faiss.StandardGpuResources()
                self.faiss_index = faiss.index_cpu_to_gpu(res, self.device.index, self.faiss_index)
        except Exception as e:
            logger.warning(f"FAISS GPU offload unavailable; using CPU index. ({e})")

    def _load_entity_db(self):
        logger.info(f"Loading entity database from {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        logger.info("Database loaded")

    def _encode_text(self, texts: List[str], mention_offsets: List[List[int]],
                     mention_lengths: List[List[int]]) -> Tuple[torch.Tensor, List[bool]]:
        """
        Encode text and extract mention representations.

        Args:
            texts: List of input texts
            mention_offsets: List of mention start positions for each text
            mention_lengths: List of mention lengths for each text

        Returns:
            Tuple of (valid mention representations, valid mask per input text)
        """
        # Prepare batch
        batch = {
            "texts": texts,
            "mention_offsets": mention_offsets,
            "mention_lengths": mention_lengths,
        }

        # Transform inputs
        model_inputs = self.transform(batch)
        token_ids = model_inputs["input_ids"].to(self.device)
        mention_offsets_tensor = model_inputs["mention_offsets"]
        mention_lengths_tensor = model_inputs["mention_lengths"]

        with torch.no_grad():
            # Encode text
            _, text_encodings = self.task.encoder(token_ids)
            text_encodings = self.task.project_encoder_op(text_encodings)

            # Extract mention representations
            mention_representations = self.task.span_encoder(
                text_encodings, mention_offsets_tensor, mention_lengths_tensor
            )

            # Filter out empty mentions
            valid_mentions = mention_representations[mention_lengths_tensor != 0]
            valid_mask = mention_lengths_tensor != 0
            if valid_mask.dim() > 1:
                valid_mask = valid_mask.any(dim=1)
            valid_mask = valid_mask.detach().cpu().tolist()

        return valid_mentions, valid_mask

    def _search_candidates(self, mention_representations: torch.Tensor, k: int = 1) -> Tuple[
        torch.Tensor, torch.Tensor]:
        """
        Search for entity candidates using FAISS index.

        Args:
            mention_representations: Tensor of mention representations
            k: Number of candidates to retrieve

        Returns:
            Tuple of (scores, indices)
        """
        scores, indices = self.faiss_index.search(mention_representations.detach().cpu().numpy(), k=k)
        return torch.from_numpy(scores).to(self.device), torch.from_numpy(indices).to(self.device)

    def get_entity_info(self, lang, entity_id):
        supported_lang = ["en", "fr", "sv", "it", "de", "nl", "fi"]
        if lang not in supported_lang:
            raise Exception("lang must be one of the following iso-codes: en, de, fr, it, nl, fi, sv")
        
        table_name = f"{lang}wiki"
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            SELECT 
                t1.id,
                t1.wikidata_qid,
                t1.type_,
                t1.min_date,
                t2.label,
                t2.descr
            FROM entities t1
            LEFT JOIN {} t2 ON t1.id = t2.id
            WHERE t1.id = ?;
            '''.format(table_name), (entity_id,))
            results = cursor.fetchall()
            if not results:
                logger.warning(f"Entity ID {entity_id} not found in {lang}wiki")
                return (entity_id, None, None, None, "UNKNOWN", "Not found")
            return results[0]
        except Exception as e:
            logger.error(f"Error fetching entity {entity_id} in {lang}: {e}")
            return (entity_id, None, None, None, "ERROR", str(e))

    def get_candidates_batch(self,
                texts: List[str],
                mention_offsets: List[List[int]],
                mention_lengths: List[List[int]],
                k: int = 10,
                lang: str = "en"
        ) -> List[List[Dict[str, Any]]]:
            """
            Get top-k candidates in a batch of texts.

            Args:
                texts: List of input texts
                mention_offsets: List of mention start positions for each text
                mention_lengths: List of mention lengths for each text

            Returns:
                List of predictions for each text, where each prediction contains:
                - start_pos: Start position of the mention
                - end_pos: End position of the mention
                - entity: Predicted entity ID
                - score: Confidence score
            """
            # Encode mentions (returns only valid mentions, filters empty ones)
            mention_representations, valid_mask = self._encode_text(
                texts, mention_offsets, mention_lengths
            )

            if len(valid_mask) != len(texts):
                logger.warning("Valid mask length mismatch; falling back to input lengths")
                valid_mask = [bool(lengths and lengths[0] > 0) for lengths in mention_lengths]

            if mention_representations.numel() == 0:
                return [[] for _ in texts]

            # Search for candidates (only for valid mentions)
            scores, indices = self._search_candidates(mention_representations, k=k)
            scores, indices = scores.tolist(), indices.tolist()

            # Format predictions - track valid mention index separately
            predictions = []
            valid_idx = 0  # Index into results (scores/indices)
            
            for is_valid in valid_mask:
                candidates = []
                
                if is_valid:  # Valid mention per model inputs
                    if valid_idx >= len(scores):
                        logger.warning(
                            "Valid mentions exceed FAISS results; skipping remaining valid mentions"
                        )
                    else:
                        ex_indices = indices[valid_idx]
                        ex_scores = scores[valid_idx]
                        for index, score in zip(ex_indices, ex_scores):
                            try:
                                candidate_info = self.get_entity_info(lang, index)
                                candidates.append({
                                    "wb_id": candidate_info[1],
                                    "type": candidate_info[2] if candidate_info[2] else "",
                                    "min_date": candidate_info[3] if candidate_info[3] else "",
                                    "label": candidate_info[4].replace("_", " ") if candidate_info[4] else "",
                                    "descr": candidate_info[5] if candidate_info[5] else "",
                                    "score": score
                                })
                            except (IndexError, TypeError) as e:
                                logger.warning(f"Failed to fetch entity info for index {index}: {e}")
                                continue
                        valid_idx += 1  # Only increment for valid mentions
                
                predictions.append(candidates)

            return predictions


# Convenience function for the original interface
def load_disambiguator(
        models_path: str = "./models",
        device: str = "cuda:0",
        embedding_dim: int = 300
):
    checkpoint_path = os.path.join(models_path, "model_wiki.ckpt")
    faiss_index_path = os.path.join(models_path, "faiss.index")
    wikidata_index_path = os.path.join(models_path, "index.txt")
    db_path = os.path.join(models_path, "knowledge_base.sqlite")

    return EntityDisambiguator(
        checkpoint_path=checkpoint_path,
        faiss_index_path=faiss_index_path,
        wikidata_index_path=wikidata_index_path,
        db_path=db_path,
        device=device,
        embedding_dim=embedding_dim
    )