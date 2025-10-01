"""Shared utility constants for the Human Evaluation Tool backend."""

from __future__ import annotations

from typing import Final

CATEGORY_NAME: Final[dict[str, str]] = {
    "000": "no-error",
    "A01": "Accuracy/Mistranslation",
    "A02": "Accuracy/PositiveNegative",
    "A03": "Accuracy/Numbers",
    "A04": "Accuracy/Pronoun",
    "A05": "Accuracy/UniqueNoun",
    "A06": "Accuracy/Omission",
    "A07": "Accuracy/Addition",
    "A08": "Accuracy/Untranslated",
    "A09": "Accuracy/Others",
    "F01": "Fluency/Spelling",
    "F02": "Fluency/WrongKanji",
    "F03": "Fluency/Grammar",
    "F04": "Fluency/Misuse",
    "F05": "Fluency/Collocation",
    "F06": "Fluency/GrammarRegister",
    "F07": "Fluency/Ambiguity",
    "F08": "Fluency/Unintelligible",
    "F09": "Fluency/Symbols",
    "F10": "Fluency/Others",
    "T01": "Terminology/Termbase",
    "T02": "Terminology/Domain",
    "T03": "Terminology/Inconsistent",
    "T04": "Terminology/Others",
    "S01": "Style/Inconsistent",
    "S02": "Style/Register",
    "S03": "Style/Inconsistent",
    "S04": "Style/Others",
    "L01": "LocaleConvention",
    "SE1": "SourceError",
}

SEVERITY_NAME: Final[dict[str, str]] = {
    "no-error": "no-error",
    "critical": "Critical",
    "minor": "Minor",
    "major": "Major",
    "not-judgeable": "NotJudgeable",
}
