from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from human_evaluation_tool import db


def _request(client, method: str, url: str, **kwargs):
    return getattr(client, method)(url, **kwargs)


def test_evaluation_crud_flow(auth_client, create_evaluation):
    client, _ = auth_client
    create_evaluation(name="Existing Eval")

    list_response = _request(client, "get", "/api/evaluations")
    assert list_response.status_code == 200
    assert len(list_response.get_json()) == 1

    create_response = _request(
        client,
        "post",
        "/api/evaluations",
        json={"name": "New Eval", "type": "error-marking", "isFinished": True},
    )
    assert create_response.status_code == 201
    evaluation_id = create_response.get_json()["id"]

    read_response = _request(client, "get", f"/api/evaluations/{evaluation_id}")
    assert read_response.status_code == 200

    update_response = _request(
        client,
        "put",
        f"/api/evaluations/{evaluation_id}",
        json={"name": "Updated Eval", "type": "error-marking", "isFinished": False},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["name"] == "Updated Eval"

    delete_response = _request(client, "delete", f"/api/evaluations/{evaluation_id}")
    assert delete_response.status_code == 204


def test_evaluation_create_missing_field(auth_client):
    client, _ = auth_client
    response = _request(client, "post", "/api/evaluations", json={"name": "Missing"})
    assert response.status_code == 422


def test_evaluation_create_duplicate(auth_client, create_evaluation):
    client, _ = auth_client
    evaluation = create_evaluation(name="Duplicate Eval")
    response = _request(
        client,
        "post",
        "/api/evaluations",
        json={"name": evaluation.name, "type": "error-marking"},
    )
    assert response.status_code == 409


def test_evaluation_read_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/evaluations/999")
    assert response.status_code == 404


def test_evaluation_annotations(auth_client, create_evaluation, create_annotation, create_bitext):
    client, user = auth_client
    evaluation = create_evaluation(name="Annotation Eval")
    bitext = create_bitext()
    create_annotation(user=user, evaluation=evaluation, bitext=bitext, is_annotated=True)
    response = _request(client, "get", f"/api/evaluations/{evaluation.id}/annotations")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1


def test_evaluation_annotations_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/evaluations/999/annotations")
    assert response.status_code == 404


def test_evaluation_results(
    auth_client,
    create_evaluation,
    create_annotation,
    create_annotation_system,
    create_marking,
    create_system,
    create_bitext,
):
    client, user = auth_client
    evaluation = create_evaluation(name="Results Eval")
    bitext = create_bitext(source="This is source", target="Target text")
    annotation = create_annotation(user=user, evaluation=evaluation, bitext=bitext, comment="Comment")
    system = create_system(name="Results System")
    annotation_system = create_annotation_system(annotation=annotation, system=system, translation="Translated text")
    create_marking(
        annotation=annotation,
        system=system,
        error_start=0,
        error_end=0,
        error_category="A01",
        error_severity="critical",
        is_source=True,
    )
    create_marking(
        annotation=annotation,
        system=system,
        error_start=0,
        error_end=0,
        error_category="F01",
        error_severity="minor",
        is_source=False,
    )

    response = _request(client, "get", f"/api/evaluations/{evaluation.id}/results")
    assert response.status_code == 200
    results = response.get_json()
    assert any("Accuracy/Mistranslation" in row for row in results)
    assert any("Fluency/Spelling" in row for row in results)


def test_evaluation_results_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/evaluations/999/results")
    assert response.status_code == 404


def test_evaluation_update_missing_field(auth_client, create_evaluation):
    client, _ = auth_client
    evaluation = create_evaluation(name="Missing Update Eval")
    response = _request(client, "put", f"/api/evaluations/{evaluation.id}", json={"name": "Only"})
    assert response.status_code == 422


def test_evaluation_update_duplicate(auth_client, create_evaluation):
    client, _ = auth_client
    first = create_evaluation(name="First Eval")
    second = create_evaluation(name="Second Eval")
    response = _request(
        client,
        "put",
        f"/api/evaluations/{second.id}",
        json={"name": first.name, "type": "error-marking"},
    )
    assert response.status_code == 409


def test_evaluation_update_not_found(auth_client):
    client, _ = auth_client
    response = _request(
        client,
        "put",
        "/api/evaluations/999",
        json={"name": "Missing", "type": "error-marking"},
    )
    assert response.status_code == 404


def test_evaluation_delete_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "delete", "/api/evaluations/999")
    assert response.status_code == 404


def test_evaluation_database_errors(auth_client, monkeypatch):
    client, _ = auth_client

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "post",
        "/api/evaluations",
        json={"name": "Error Eval", "type": "error-marking"},
    )
    assert response.status_code == 500


def test_evaluation_update_delete_database_errors(auth_client, create_evaluation, monkeypatch):
    client, _ = auth_client
    evaluation = create_evaluation(name="DB Eval")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    update_response = _request(
        client,
        "put",
        f"/api/evaluations/{evaluation.id}",
        json={"name": evaluation.name, "type": evaluation.type},
    )
    assert update_response.status_code == 500

    delete_response = _request(client, "delete", f"/api/evaluations/{evaluation.id}")
    assert delete_response.status_code == 500
