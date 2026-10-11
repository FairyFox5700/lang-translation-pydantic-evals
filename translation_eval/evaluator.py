"""Deterministic translation checks suitable for CI smoke tests."""

from __future__ import annotations

import re

from .models import (
    EvalCheck,
    EvaluationCase,
    EvaluationPair,
    EvaluationResult,
    SuiteSummary,
    TranslationOutput,
)

_PLACEHOLDER = re.compile(r"\{\{\s*[^{}]+?\s*\}\}")
_NUMBER = re.compile(r"(?<!\w)\d+(?:[.,]\d+)?(?!\w)")


def _check(name: str, passed: bool, details: str) -> EvalCheck:
    return EvalCheck(name=name, passed=passed, details=details)


def evaluate_translation(
    case: EvaluationCase, output: TranslationOutput
) -> EvaluationResult:
    """Evaluate invariants; semantic quality still needs a human or model judge."""
    EvaluationPair(case=case, output=output)

    source_placeholders = set(_PLACEHOLDER.findall(case.source_text))
    output_placeholders = set(_PLACEHOLDER.findall(output.translated_text))
    source_numbers = set(_NUMBER.findall(case.source_text))
    output_numbers = set(_NUMBER.findall(output.translated_text))

    missing_terms = [
        target
        for source, target in case.required_terms.items()
        if source.casefold() in case.source_text.casefold()
        and target.casefold() not in output.translated_text.casefold()
    ]

    checks = [
        _check(
            "non_empty",
            bool(output.translated_text.strip()),
            "translation contains visible text",
        ),
        _check(
            "placeholders_preserved",
            source_placeholders == output_placeholders,
            f"expected {sorted(source_placeholders)}; got {sorted(output_placeholders)}",
        ),
        _check(
            "numbers_preserved",
            source_numbers == output_numbers,
            f"expected {sorted(source_numbers)}; got {sorted(output_numbers)}",
        ),
        _check(
            "required_terms_used",
            not missing_terms,
            "missing: " + ", ".join(missing_terms) if missing_terms else "all required terms used",
        ),
    ]
    score = sum(item.passed for item in checks) / len(checks)
    return EvaluationResult(
        case_id=case.id,
        passed=all(item.passed for item in checks),
        score=score,
        checks=checks,
    )


def evaluate_suite(
    cases: list[EvaluationCase], outputs: list[TranslationOutput]
) -> SuiteSummary:
    """Match outputs by case ID and aggregate individual results."""
    output_by_id = {output.case_id: output for output in outputs}
    if len(output_by_id) != len(outputs):
        raise ValueError("output case_id values must be unique")

    missing = [case.id for case in cases if case.id not in output_by_id]
    if missing:
        raise ValueError(f"missing outputs for cases: {', '.join(missing)}")

    results = [evaluate_translation(case, output_by_id[case.id]) for case in cases]
    total = len(results)
    passed = sum(result.passed for result in results)
    return SuiteSummary(
        total=total,
        passed=passed,
        pass_rate=passed / total if total else 0.0,
        average_score=(sum(result.score for result in results) / total if total else 0.0),
        results=results,
    )
