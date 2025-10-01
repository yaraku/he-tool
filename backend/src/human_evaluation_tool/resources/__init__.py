"""Resource registration helpers."""

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
