"""User model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .annotation import Annotation


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    nativeLanguage: Mapped[str] = mapped_column(String(2), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "nativeLanguage": self.nativeLanguage,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
