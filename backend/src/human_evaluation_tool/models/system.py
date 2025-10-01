"""System model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .annotation_system import AnnotationSystem
    from .marking import Marking


class System(Base):
    __tablename__ = "system"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    annotation_systems: Mapped[list["AnnotationSystem"]] = relationship(
        "AnnotationSystem", back_populates="system", cascade="all, delete-orphan"
    )
    markings: Mapped[list["Marking"]] = relationship(
        "Marking", back_populates="system", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
