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

# Resource registration helpers.

from __future__ import annotations

from flask import Flask

from . import annotation, bitext, document, evaluation, marking, system, user


def register_resources(app: Flask) -> None:
    """Register all resource blueprints with the Flask app."""

    for blueprint in (
        annotation.bp,
        bitext.bp,
        document.bp,
        evaluation.bp,
        marking.bp,
        system.bp,
        user.bp,
    ):
        app.register_blueprint(blueprint)


__all__ = ["register_resources"]
