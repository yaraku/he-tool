"""
Copyright (C) 2023-2025 Yaraku, Inc.

This file is part of Human Evaluation Tool.

Human Evaluation Tool is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

Human Evaluation Tool is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
Human Evaluation Tool. If not, see <https://www.gnu.org/licenses/>.

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, August 2023
"""

from __future__ import annotations

from typing import Final


CATEGORY_NAME: Final[dict[str, str]] = {
    "000": "No Error",
    "A01": "Accuracy/Mistranslation",
    "A02": "Accuracy/Positive/Negative",
    "A03": "Accuracy/Numbers",
    "A04": "Accuracy/Pronoun",
    "A05": "Accuracy/Proper Noun",
    "A06": "Accuracy/Omission",
    "A07": "Accuracy/Addition",
    "A08": "Accuracy/Untranslated",
    "A09": "Accuracy/Others",
    "F01": "Fluency/Typography/Spelling",
    "F02": "Fluency/Wrong Kanji",
    "F03": "Fluency/Grammar",
    "F04": "Fluency/Misuse",
    "F05": "Fluency/Collocation",
    "F06": "Fluency/Grammar Register",
    "F07": "Fluency/Ambiguity",
    "F08": "Fluency/Unintelligible",
    "F09": "Fluency/Symbols",
    "F10": "Fluency/Others",
    "T01": "Terminology/Inconsistent with termbase",
    "T02": "Terminology/Inconsistent with domain",
    "T03": "Terminology/Inconsistent use",
    "T04": "Terminology/Others",
    "S01": "Style/Inconsistent with company style",
    "S02": "Style/Register",
    "S03": "Style/Inconsistent style",
    "S04": "Style/Others",
    "L01": "Locale/Locale convention",
    "SE1": "SourceError/Source Error",
}

SEVERITY_NAME: Final[dict[str, str]] = {
    "no-error": "no-error",
    "critical": "Critical",
    "minor": "Minor",
    "major": "Major",
    "not-judgeable": "NotJudgeable",
}
