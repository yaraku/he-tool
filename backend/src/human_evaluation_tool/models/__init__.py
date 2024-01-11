"""
Copyright (C) 2023 Yaraku, Inc.

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

from .annotation import Annotation
from .annotation_system import AnnotationSystem
from .bitext import Bitext
from .document import Document
from .evaluation import Evaluation
from .marking import Marking
from .system import System
from .user import User


__all__ = [
    "Annotation",
    "AnnotationSystem",
    "Bitext",
    "Document",
    "Evaluation",
    "Marking",
    "System",
    "User",
]
