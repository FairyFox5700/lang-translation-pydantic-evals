"""Pydantic models for translation evaluation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EvaluationCase(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    source_text: str = Field(min_length=1)
    source_language: str = Field(pattern=r"^[a-z]{2}(?:-[A-Z]{2})?$")
    target_language: str = Field(pattern=r"^[a-z]{2}(?:-[A-Z]{2})?$")
    required_terms: dict[str, str] = Field(default_factory=dict)


class TranslationOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    case_id: str = Field(min_length=1)
    translated_text: str
    target_language: str = Field(pattern=r"^[a-z]{2}(?:-[A-Z]{2})?$")


class EvaluationPair(BaseModel):
    model_config = ConfigDict(frozen=True)

    case: EvaluationCase
    output: TranslationOutput

    @model_validator(mode="after")
    def identifiers_and_languages_match(self) -> "EvaluationPair":
        if self.case.id != self.output.case_id:
            raise ValueError("output case_id must match case id")
        if self.case.target_language != self.output.target_language:
            raise ValueError("output target language must match the evaluation case")
        return self


class EvalCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    passed: bool
    details: str


class EvaluationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    case_id: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    checks: list[EvalCheck]


class SuiteSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    total: int = Field(ge=0)
    passed: int = Field(ge=0)
    pass_rate: float = Field(ge=0.0, le=1.0)
    average_score: float = Field(ge=0.0, le=1.0)
    results: list[EvaluationResult]
