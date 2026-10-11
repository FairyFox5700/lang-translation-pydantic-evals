import json
import subprocess
import sys

import pytest
from pydantic import ValidationError

from translation_eval.models import EvaluationCase, EvaluationPair, TranslationOutput
from translation_eval.evaluator import evaluate_translation, evaluate_suite


def test_models_reject_wrong_output_language():
    case = EvaluationCase(
        id="greeting",
        source_text="Hello {{name}}",
        source_language="en",
        target_language="fr-CA",
        required_terms={"Hello": "Bonjour"},
    )

    with pytest.raises(ValidationError):
        EvaluationPair(
            case=case,
            output=TranslationOutput(
                case_id=case.id,
                translated_text="Bonjour {{name}}",
                target_language="es-MX",
            ),
        )


def test_evaluator_passes_translation_that_preserves_contract():
    case = EvaluationCase(
        id="invoice",
        source_text="Hello {{name}}, invoice 104 is ready.",
        source_language="en",
        target_language="fr-CA",
        required_terms={"invoice": "facture"},
    )
    output = TranslationOutput(
        case_id="invoice",
        translated_text="Bonjour {{name}}, la facture 104 est prête.",
        target_language="fr-CA",
    )

    result = evaluate_translation(case, output)

    assert result.passed is True
    assert result.score == 1.0
    assert all(check.passed for check in result.checks)


def test_evaluator_reports_missing_placeholder_term_and_number():
    case = EvaluationCase(
        id="invoice",
        source_text="Hello {{name}}, invoice 104 is ready.",
        source_language="en",
        target_language="fr-CA",
        required_terms={"invoice": "facture"},
    )
    output = TranslationOutput(
        case_id="invoice",
        translated_text="Bonjour, le document est prêt.",
        target_language="fr-CA",
    )

    result = evaluate_translation(case, output)

    assert result.passed is False
    assert result.score == 0.25
    assert {check.name for check in result.checks if not check.passed} == {
        "placeholders_preserved",
        "numbers_preserved",
        "required_terms_used",
    }


def test_suite_summary_aggregates_results():
    cases = [
        EvaluationCase(
            id="a",
            source_text="Order 7 for {{name}}",
            source_language="en",
            target_language="de-DE",
        ),
        EvaluationCase(
            id="b",
            source_text="Order 8",
            source_language="en",
            target_language="de-DE",
        ),
    ]
    outputs = [
        TranslationOutput(
            case_id="a",
            translated_text="Bestellung 7 für {{name}}",
            target_language="de-DE",
        ),
        TranslationOutput(
            case_id="b",
            translated_text="Bestellung neun",
            target_language="de-DE",
        ),
    ]

    summary = evaluate_suite(cases, outputs)

    assert summary.total == 2
    assert summary.passed == 1
    assert summary.pass_rate == 0.5
    assert summary.average_score == 0.875


def test_example_script_outputs_machine_readable_summary():
    completed = subprocess.run(
        [sys.executable, "example.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["total"] == 2
    assert payload["passed"] == 1
    assert payload["pass_rate"] == 0.5
