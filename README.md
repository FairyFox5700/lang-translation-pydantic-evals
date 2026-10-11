# Pydantic translation evals

A small, dependency-light example showing how to:

- validate translation test cases and model outputs with Pydantic 2;
- enforce matching case IDs and target locales;
- evaluate preserved `{{placeholders}}`, numbers, and required glossary terms;
- aggregate case results into a JSON suite report.

These are deterministic **contract checks**, not a complete measure of translation quality. Add native-speaker review or a separately calibrated model judge for meaning, fluency, tone, and cultural fit.

## Run

```bash
python -m venv .venv
# Windows
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe example.py
.venv/Scripts/python.exe -m pytest -q
```

On macOS/Linux, use `.venv/bin/python` instead.

## Main API

```python
case = EvaluationCase(
    id="invoice",
    source_text="Invoice 104 for {{name}}",
    source_language="en",
    target_language="fr-CA",
    required_terms={"Invoice": "facture"},
)
output = TranslationOutput(
    case_id="invoice",
    translated_text="Facture 104 pour {{name}}",
    target_language="fr-CA",
)
result = evaluate_translation(case, output)
```

A case passes only when every configured check passes. `score` is the fraction of passed checks.
