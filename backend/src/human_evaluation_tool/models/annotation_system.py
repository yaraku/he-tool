"""Annotation-system mapping model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base

if TYPE_CHECKING:  # pragma: no cover
    from .annotation import Annotation
    from .system import System


class AnnotationSystem(Base):
    __tablename__ = "annotation_system"

    id: Mapped[int] = mapped_column(primary_key=True)
    annotationId: Mapped[int] = mapped_column(ForeignKey("annotation.id"), nullable=False)
    systemId: Mapped[int] = mapped_column(ForeignKey("system.id"), nullable=False)
    translation: Mapped[str | None] = mapped_column(Text)
    createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    annotation: Mapped["Annotation"] = relationship(
        "Annotation", back_populates="annotation_systems"
    )
    system: Mapped["System"] = relationship("System", back_populates="annotation_systems")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "annotationId": self.annotationId,
            "systemId": self.systemId,
            "translation": self.translation,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
