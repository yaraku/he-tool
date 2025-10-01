"""Annotation model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base

if TYPE_CHECKING:  # pragma: no cover
    from .annotation_system import AnnotationSystem
    from .bitext import Bitext
    from .evaluation import Evaluation
    from .marking import Marking
    from .user import User


class Annotation(Base):
    __tablename__ = "annotation"

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    evaluationId: Mapped[int] = mapped_column(ForeignKey("evaluation.id"), nullable=False)
    bitextId: Mapped[int] = mapped_column(ForeignKey("bitext.id"), nullable=False)
    isAnnotated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="annotations")
    evaluation: Mapped["Evaluation"] = relationship(
        "Evaluation", back_populates="annotations"
    )
    bitext: Mapped["Bitext"] = relationship("Bitext", back_populates="annotations")
    annotation_systems: Mapped[list["AnnotationSystem"]] = relationship(
        "AnnotationSystem", back_populates="annotation", cascade="all, delete-orphan"
    )
    markings: Mapped[list["Marking"]] = relationship(
        "Marking", back_populates="annotation", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.userId,
            "evaluation": self.evaluation.to_dict(),
            "bitext": self.bitext.to_dict(),
            "isAnnotated": self.isAnnotated,
            "comment": self.comment,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
