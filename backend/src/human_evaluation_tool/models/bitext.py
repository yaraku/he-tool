"""Bitext model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base

if TYPE_CHECKING:  # pragma: no cover
    from .annotation import Annotation
    from .document import Document


class Bitext(Base):
    __tablename__ = "bitext"

    id: Mapped[int] = mapped_column(primary_key=True)
    documentId: Mapped[int] = mapped_column(ForeignKey("document.id"), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    target: Mapped[str | None] = mapped_column(Text)
    createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="bitexts")
    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation", back_populates="bitext", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "documentId": self.documentId,
            "source": self.source,
            "target": self.target,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
