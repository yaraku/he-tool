"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password", sa.String(length=60), nullable=False),
        sa.Column("nativeLanguage", sa.String(length=2), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "document",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "evaluation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("isFinished", sa.Boolean(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "system",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "bitext",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("documentId", sa.Integer(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("target", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["documentId"], ["document.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "annotation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("userId", sa.Integer(), nullable=False),
        sa.Column("evaluationId", sa.Integer(), nullable=False),
        sa.Column("bitextId", sa.Integer(), nullable=False),
        sa.Column("isAnnotated", sa.Boolean(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["bitextId"], ["bitext.id"]),
        sa.ForeignKeyConstraint(["evaluationId"], ["evaluation.id"]),
        sa.ForeignKeyConstraint(["userId"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "annotation_system",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("annotationId", sa.Integer(), nullable=False),
        sa.Column("systemId", sa.Integer(), nullable=False),
        sa.Column("translation", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["annotationId"], ["annotation.id"]),
        sa.ForeignKeyConstraint(["systemId"], ["system.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "marking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("annotationId", sa.Integer(), nullable=False),
        sa.Column("systemId", sa.Integer(), nullable=False),
        sa.Column("errorStart", sa.Integer(), nullable=False),
        sa.Column("errorEnd", sa.Integer(), nullable=False),
        sa.Column("errorCategory", sa.String(length=20), nullable=False),
        sa.Column("errorSeverity", sa.String(length=20), nullable=False),
        sa.Column("isSource", sa.Boolean(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["annotationId"], ["annotation.id"]),
        sa.ForeignKeyConstraint(["systemId"], ["system.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("marking")
    op.drop_table("annotation_system")
    op.drop_table("annotation")
    op.drop_table("bitext")
    op.drop_table("system")
    op.drop_table("evaluation")
    op.drop_table("document")
    op.drop_table("user")
