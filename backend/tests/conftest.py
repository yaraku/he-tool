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

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, October 2025
"""

import os
from collections.abc import Callable, Iterator
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.pool import StaticPool


os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("DB_PASSWORD", "password")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "testuser")
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")

from human_evaluation_tool import bcrypt, create_app, db  # noqa: E402
from human_evaluation_tool.models import (  # noqa: E402
    Annotation,
    AnnotationSystem,
    Bitext,
    Document,
    Evaluation,
    Marking,
    System,
    User,
)


UserFactory = Callable[..., User]
SystemFactory = Callable[..., System]
DocumentFactory = Callable[..., Document]
BitextFactory = Callable[..., Bitext]
EvaluationFactory = Callable[..., Evaluation]
AnnotationFactory = Callable[..., Annotation]
AnnotationSystemFactory = Callable[..., AnnotationSystem]
MarkingFactory = Callable[..., Marking]
AuthClient = tuple[FlaskClient, User]


def _now() -> datetime:
    return datetime(2023, 1, 1, 12, 0, 0)


@pytest.fixture(scope="session")
def app() -> Iterator[Flask]:
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,
            },
            "JWT_COOKIE_CSRF_PROTECT": False,
        }
    )

    with application.app_context():
        db.session.remove()
        db.engine.dispose()
        yield application


@pytest.fixture(autouse=True)
def _reset_database(app: Flask) -> Iterator[None]:
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def create_user() -> UserFactory:
    def _create_user(
        email: str = "user@example.com",
        password: str = "password",
        native_language: str = "en",
    ) -> User:
        user = User(
            email=email,
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
            nativeLanguage=native_language,
            createdAt=_now(),
            updatedAt=_now(),
        )
        db.session.add(user)
        db.session.commit()
        return user

    return _create_user


@pytest.fixture
def auth_client(client: FlaskClient, create_user: UserFactory) -> AuthClient:
    user = create_user()
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password", "remember": False},
    )
    assert response.status_code == 200
    return client, user


@pytest.fixture
def create_system() -> SystemFactory:
    def _create_system(name: str = "System A") -> System:
        system = System(name=name, createdAt=_now(), updatedAt=_now())
        db.session.add(system)
        db.session.commit()
        return system

    return _create_system


@pytest.fixture
def create_document() -> DocumentFactory:
    def _create_document(name: str = "Doc A") -> Document:
        document = Document(name=name, createdAt=_now(), updatedAt=_now())
        db.session.add(document)
        db.session.commit()
        return document

    return _create_document


@pytest.fixture
def create_bitext(create_document: DocumentFactory) -> BitextFactory:
    def _create_bitext(
        document: Document | None = None,
        source: str = "Hello",
        target: str = "World",
    ) -> Bitext:
        document = document or create_document()
        bitext = Bitext(
            documentId=document.id,
            source=source,
            target=target,
            createdAt=_now(),
            updatedAt=_now(),
        )
        db.session.add(bitext)
        db.session.commit()
        return bitext

    return _create_bitext


@pytest.fixture
def create_evaluation() -> EvaluationFactory:
    def _create_evaluation(
        name: str = "Eval A",
        eval_type: str = "error-marking",
        is_finished: bool = False,
    ) -> Evaluation:
        evaluation = Evaluation(
            name=name,
            type=eval_type,
            isFinished=is_finished,
            createdAt=_now(),
            updatedAt=_now(),
        )
        db.session.add(evaluation)
        db.session.commit()
        return evaluation

    return _create_evaluation


@pytest.fixture
def create_annotation(
    create_user: UserFactory,
    create_evaluation: EvaluationFactory,
    create_bitext: BitextFactory,
) -> AnnotationFactory:
    def _create_annotation(
        user: User | None = None,
        evaluation: Evaluation | None = None,
        bitext: Bitext | None = None,
        is_annotated: bool = False,
        comment: str | None = None,
    ) -> Annotation:
        user = user or create_user(email="annotator@example.com")
        evaluation = evaluation or create_evaluation(name="Eval B")
        bitext = bitext or create_bitext()
        annotation = Annotation(
            userId=user.id,
            evaluationId=evaluation.id,
            bitextId=bitext.id,
            isAnnotated=is_annotated,
            comment=comment,
            createdAt=_now(),
            updatedAt=_now(),
        )
        db.session.add(annotation)
        db.session.commit()
        return annotation

    return _create_annotation


@pytest.fixture
def create_annotation_system(
    create_annotation: AnnotationFactory,
    create_system: SystemFactory,
) -> AnnotationSystemFactory:
    def _create_annotation_system(
        annotation: Annotation | None = None,
        system: System | None = None,
        translation: str = "Translated",
    ) -> AnnotationSystem:
        annotation = annotation or create_annotation()
        system = system or create_system()
        annotation_system = AnnotationSystem(
            annotationId=annotation.id,
            systemId=system.id,
            translation=translation,
            createdAt=_now(),
            updatedAt=_now(),
        )
        db.session.add(annotation_system)
        db.session.commit()
        return annotation_system

    return _create_annotation_system


@pytest.fixture
def create_marking(
    create_annotation: AnnotationFactory,
    create_system: SystemFactory,
) -> MarkingFactory:
    def _create_marking(
        annotation: Annotation | None = None,
        system: System | None = None,
        error_start: int = 0,
        error_end: int = 0,
        error_category: str = "A01",
        error_severity: str = "critical",
        is_source: bool = True,
    ) -> Marking:
        annotation = annotation or create_annotation()
        system = system or create_system(name="System B")
        marking = Marking(
            annotationId=annotation.id,
            systemId=system.id,
            errorStart=error_start,
            errorEnd=error_end,
            errorCategory=error_category,
            errorSeverity=error_severity,
            isSource=is_source,
            createdAt=_now(),
            updatedAt=_now(),
        )
        db.session.add(marking)
        db.session.commit()
        return marking

    return _create_marking
