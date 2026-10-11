"""Run two sample translations through the deterministic eval suite."""

from translation_eval import EvaluationCase, TranslationOutput, evaluate_suite

cases = [
    EvaluationCase(
        id="good",
        source_text="Hello {{name}}, invoice 104 is ready.",
        source_language="en",
        target_language="fr-CA",
        required_terms={"invoice": "facture"},
    ),
    EvaluationCase(
        id="bad",
        source_text="Order 8 is ready.",
        source_language="en",
        target_language="fr-CA",
        required_terms={"Order": "commande"},
    ),
]

outputs = [
    TranslationOutput(
        case_id="good",
        translated_text="Bonjour {{name}}, la facture 104 est prête.",
        target_language="fr-CA",
    ),
    TranslationOutput(
        case_id="bad",
        translated_text="Le document 8 est prêt.",
        target_language="fr-CA",
    ),
]

print(evaluate_suite(cases, outputs).model_dump_json(indent=2))
