# Domain Model

The Human Evaluation Tool manages translation evaluation projects. The database schema is centred on annotations performed by users on bitext pairs, enriched with system outputs and marking metadata.

## Entity-relationship diagram

```mermaid
erDiagram
    USER ||--o{ ANNOTATION : annotates
    USER {
        int id PK
        string email
        string password
        string nativeLanguage
        datetime createdAt
        datetime updatedAt
    }

    EVALUATION ||--o{ ANNOTATION : contains
    EVALUATION {
        int id PK
        string name
        string type
        bool isFinished
        datetime createdAt
        datetime updatedAt
    }

    DOCUMENT ||--o{ BITEXT : owns
    DOCUMENT {
        int id PK
        string name
        datetime createdAt
        datetime updatedAt
    }

    BITEXT ||--o{ ANNOTATION : referenced
    BITEXT {
        int id PK
        int documentId FK
        string source
        string target
        datetime createdAt
        datetime updatedAt
    }

    ANNOTATION ||--o{ ANNOTATION_SYSTEM : produces
    ANNOTATION ||--o{ MARKING : flaggedBy
    ANNOTATION {
        int id PK
        int userId FK
        int evaluationId FK
        int bitextId FK
        bool isAnnotated
        string comment
        datetime createdAt
        datetime updatedAt
    }

    SYSTEM ||--o{ ANNOTATION_SYSTEM : outputs
    SYSTEM ||--o{ MARKING : referencedBy
    SYSTEM {
        int id PK
        string name
        datetime createdAt
        datetime updatedAt
    }

    ANNOTATION_SYSTEM {
        int id PK
        int annotationId FK
        int systemId FK
        string translation
        datetime createdAt
        datetime updatedAt
    }

    MARKING {
        int id PK
        int annotationId FK
        int systemId FK
        int errorStart
        int errorEnd
        string errorCategory
        string errorSeverity
        bool isSource
        datetime createdAt
        datetime updatedAt
    }
```

## Class relationships

```mermaid
classDiagram
    class User {
        +int id
        +str email
        +str password
        +str nativeLanguage
        +datetime createdAt
        +datetime updatedAt
        +list~Annotation~ annotations
        +to_dict()
    }
    class Evaluation {
        +int id
        +str name
        +str type
        +bool isFinished
        +datetime createdAt
        +datetime updatedAt
        +list~Annotation~ annotations
        +to_dict()
    }
    class Document {
        +int id
        +str name
        +datetime createdAt
        +datetime updatedAt
        +list~Bitext~ bitexts
        +to_dict()
    }
    class Bitext {
        +int id
        +int documentId
        +str source
        +str? target
        +datetime createdAt
        +datetime updatedAt
        +Document document
        +list~Annotation~ annotations
        +to_dict()
    }
    class Annotation {
        +int id
        +int userId
        +int evaluationId
        +int bitextId
        +bool isAnnotated
        +str? comment
        +datetime createdAt
        +datetime updatedAt
        +User user
        +Evaluation evaluation
        +Bitext bitext
        +list~AnnotationSystem~ annotation_systems
        +list~Marking~ markings
        +to_dict()
    }
    class System {
        +int id
        +str name
        +datetime createdAt
        +datetime updatedAt
        +list~AnnotationSystem~ annotation_systems
        +list~Marking~ markings
        +to_dict()
    }
    class AnnotationSystem {
        +int id
        +int annotationId
        +int systemId
        +str? translation
        +datetime createdAt
        +datetime updatedAt
        +Annotation annotation
        +System system
        +to_dict()
    }
    class Marking {
        +int id
        +int annotationId
        +int systemId
        +int errorStart
        +int errorEnd
        +str errorCategory
        +str errorSeverity
        +bool isSource
        +datetime createdAt
        +datetime updatedAt
        +Annotation annotation
        +System system
        +to_dict()
    }

    User "1" --> "*" Annotation
    Evaluation "1" --> "*" Annotation
    Document "1" --> "*" Bitext
    Bitext "1" --> "*" Annotation
    Annotation "1" --> "*" AnnotationSystem
    Annotation "1" --> "*" Marking
    System "1" --> "*" AnnotationSystem
    System "1" --> "*" Marking
```

## Invariants

- `Annotation` rows require valid foreign keys to `User`, `Evaluation`, and `Bitext` records. The API validates these relationships before creation or update.
- `AnnotationSystem` rows always pair one annotation with one system translation output. The combination `(annotationId, systemId)` is effectively unique from the application’s perspective.
- `Marking` rows reference both an `Annotation` and the `System` responsible for the translation; the API enforces user ownership before allowing marking operations.
- Timestamps (`createdAt`, `updatedAt`) are managed in application code for consistency across SQLite/PostgreSQL backends.

## Derived data

The evaluation results endpoint (`GET /api/evaluations/<id>/results`) joins annotations, bitexts, annotation systems, and markings to emit TSV rows. Category and severity names are resolved through the lookup dictionaries defined in `human_evaluation_tool.utils`.
