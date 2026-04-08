"""
PhoBERT fine-tuned model loader + inference.
Load once on startup, reuse for every request.
"""

from __future__ import annotations
import os
import logging
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

MODEL_NAME = "vinai/phobert-base"
WEIGHTS_PATH = Path(__file__).parent / "weights" / "phobert_reviewtrust.pt"
MODEL_VERSION = "phobert_reviewtrust_v1"
MAX_LENGTH = 256


class ReviewClassifier:
    """
    Wrapper cho PhoBERT fine-tuned binary classifier.
    Label: 0 = fake, 1 = genuine
    """

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = self._load_model()
        self.model.eval()
        self.model.to(self.device)
        logger.info(f"ReviewClassifier loaded on {self.device}")

    def _load_model(self) -> AutoModelForSequenceClassification:
        base = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, num_labels=2
        )
        if WEIGHTS_PATH.exists():
            state_dict = torch.load(WEIGHTS_PATH, map_location=self.device)
            base.load_state_dict(state_dict)
            logger.info(f"Loaded fine-tuned weights from {WEIGHTS_PATH}")
        else:
            logger.warning(
                f"Fine-tuned weights not found at {WEIGHTS_PATH}. "
                "Using base PhoBERT (untrained). Run fine-tuning first."
            )
        return base

    def predict(self, text: str) -> tuple[float, float]:
        """
        Returns:
            genuine_prob: float 0–1 (xác suất review là thật)
            confidence:   float 0–1 (max của 2 class probabilities)
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.softmax(outputs.logits, dim=1)[0]
        genuine_prob = probs[1].item()
        confidence = probs.max().item()
        return genuine_prob, confidence

    def predict_batch(self, texts: list[str]) -> list[tuple[float, float]]:
        """Batch inference — hiệu quả hơn khi xử lý nhiều reviews cùng lúc."""
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.softmax(outputs.logits, dim=1)
        results = []
        for i in range(len(texts)):
            genuine_prob = probs[i][1].item()
            confidence = probs[i].max().item()
            results.append((genuine_prob, confidence))
        return results


# Singleton — load once, reuse
_classifier: ReviewClassifier | None = None


def get_classifier() -> ReviewClassifier:
    global _classifier
    if _classifier is None:
        _classifier = ReviewClassifier()
    return _classifier


def is_model_loaded() -> bool:
    return _classifier is not None
