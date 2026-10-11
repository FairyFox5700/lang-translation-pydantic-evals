"""Small Pydantic-based translation evaluation example."""

from .evaluator import evaluate_suite, evaluate_translation
from .models import EvaluationCase, TranslationOutput

__all__ = [
    "EvaluationCase",
    "TranslationOutput",
    "evaluate_translation",
    "evaluate_suite",
]
