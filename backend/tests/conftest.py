import os
from datetime import datetime
from typing import Callable

import pytest
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


def _now() -> datetime:
    return datetime(2023, 1, 1, 12, 0, 0)


@pytest.fixture(scope="session")
def app():
    app = create_app(
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

    with app.app_context():
        db.session.remove()
        db.engine.dispose()
        yield app


@pytest.fixture(autouse=True)
def _reset_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_user() -> Callable[[str, str, str], User]:
    def _create_user(email: str = "user@example.com", password: str = "password", native_language: str = "en") -> User:
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
def auth_client(client, create_user):
    user = create_user()
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password", "remember": False},
    )
    assert response.status_code == 200
    return client, user


@pytest.fixture
def create_system():
    def _create_system(name: str = "System A") -> System:
        system = System(name=name, createdAt=_now(), updatedAt=_now())
        db.session.add(system)
        db.session.commit()
        return system

    return _create_system


@pytest.fixture
def create_document():
    def _create_document(name: str = "Doc A") -> Document:
        document = Document(name=name, createdAt=_now(), updatedAt=_now())
        db.session.add(document)
        db.session.commit()
        return document

    return _create_document


@pytest.fixture
def create_bitext(create_document):
    def _create_bitext(document: Document | None = None, source: str = "Hello", target: str = "World") -> Bitext:
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
def create_evaluation():
    def _create_evaluation(name: str = "Eval A", eval_type: str = "error-marking", is_finished: bool = False) -> Evaluation:
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
def create_annotation(create_user, create_evaluation, create_bitext):
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
def create_annotation_system(create_annotation, create_system):
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
def create_marking(create_annotation, create_system):
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
