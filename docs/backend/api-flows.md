# API Flows

The backend exposes a REST API composed of the authentication blueprint and seven resource blueprints. This document highlights the most important interactions with Mermaid sequence diagrams and lists the available endpoints.

## Authentication – login and refresh

```mermaid
sequenceDiagram
    participant Browser
    participant AuthBP as Auth Blueprint
    participant DB as SQLAlchemy Session
    participant JWT as flask_jwt_extended

    Browser->>AuthBP: POST /api/auth/login (email, password, remember)
    AuthBP->>DB: select(User).filter_by(email)
    DB-->>AuthBP: User row
    AuthBP->>AuthBP: bcrypt.check_password_hash
    AuthBP->>JWT: create_access_token(identity=user.id, expires_delta)
    JWT-->>AuthBP: JWT string
    AuthBP-->>Browser: 200 OK + Set-Cookie(access_token_cookie)

    Note over Browser,AuthBP: Subsequent requests send the cookie automatically.

    AuthBP->>Browser: after_app_request hook inspects exp claim
    AuthBP->>JWT: get_jwt()
    AuthBP->>JWT: create_access_token(...) when near expiry
    JWT-->>AuthBP: refreshed token
    AuthBP-->>Browser: Set-Cookie with new token
```

`GET /api/auth/validate` requires a valid JWT and returns `{"success": False}` to match the existing front-end contract. `POST /api/auth/logout` clears the cookie and returns `{"success": True}`.

## Annotation lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant AnnBP as Annotation Blueprint
    participant DB as SQLAlchemy Session

    Client->>AnnBP: POST /api/annotations (userId, evaluationId, bitextId, ...)
    AnnBP->>DB: db.session.get(User, userId)
    AnnBP->>DB: db.session.get(Evaluation, evaluationId)
    AnnBP->>DB: db.session.get(Bitext, bitextId)
    DB-->>AnnBP: Valid references
    AnnBP->>DB: INSERT Annotation
    DB-->>AnnBP: Committed row
    AnnBP-->>Client: 201 Created + annotation JSON

    Client->>AnnBP: PUT /api/annotations/<id>
    AnnBP->>DB: db.session.get(Annotation, id)
    DB-->>AnnBP: Annotation instance
    AnnBP->>DB: UPDATE + commit
    AnnBP-->>Client: 200 OK + updated JSON

    Client->>AnnBP: DELETE /api/annotations/<id>
    AnnBP->>DB: db.session.get(Annotation, id)
    DB-->>AnnBP: Annotation instance
    AnnBP->>DB: DELETE + commit
    AnnBP-->>Client: 204 No Content
```

All annotation routes require JWT authentication. `GET /api/annotations` scopes results to the current user by inspecting `get_jwt_identity()`.

## Evaluation results export

```mermaid
sequenceDiagram
    participant Client
    participant EvalBP as Evaluation Blueprint
    participant DB as SQLAlchemy Session
    participant Utils as utils.CATEGORY_NAME / SEVERITY_NAME

    Client->>EvalBP: GET /api/evaluations/<id>/results
    EvalBP->>DB: db.session.get(Evaluation, id)
    DB-->>EvalBP: Evaluation or None
    EvalBP-->>Client: 404 when missing
    EvalBP->>DB: select(Annotation).filter_by(evaluationId=id)
    loop per annotation
        EvalBP->>DB: db.session.get(Bitext, annotation.bitextId)
        EvalBP->>DB: db.session.get(User, annotation.userId)
        EvalBP->>DB: select(Marking).filter_by(annotationId)
        loop per marking
            EvalBP->>DB: select(AnnotationSystem).filter_by(annotationId, systemId)
            EvalBP->>DB: db.session.get(System, marking.systemId)
            EvalBP->>Utils: CATEGORY_NAME[marking.errorCategory]
            EvalBP->>Utils: SEVERITY_NAME[marking.errorSeverity]
            EvalBP->>EvalBP: Compose TSV row (with highlighted segments)
        end
    end
    EvalBP-->>Client: 200 OK + list[str] (TSV rows)
```

When the marking references a segment in the source, the code wraps the relevant tokens with `<v>`/`</v>` markers; otherwise the translation text receives the markers. Newlines are normalised to `<br>` in both source and translation strings.

## Endpoint summary

| Blueprint | Base path | Description |
|-----------|-----------|-------------|
| `auth` | `/api/auth` | Login, logout, validate; refresh hook registered globally |
| `users` | `/api/users` | CRUD for user accounts; unique email enforcement |
| `systems` | `/api/systems` | CRUD for machine translation systems |
| `documents` | `/api/documents` | CRUD for source documents |
| `bitexts` | `/api/bitexts` | CRUD for aligned source/target segments |
| `evaluations` | `/api/evaluations` | CRUD, annotation listing, TSV export |
| `annotations` | `/api/annotations` | CRUD scoped to authenticated user |
| `markings` | `/api/annotations/<annotation_id>/markings` and `/api/annotations/<annotation_id>/systems/<system_id>/markings` | Marking collection and per-system CRUD with ownership checks |

All resource blueprints enforce JWT authentication via `@jwt_required()`; the tests use fixtures to issue valid cookies for authenticated scenarios.
