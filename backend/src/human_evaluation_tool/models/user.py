"""Copyright (C) 2023 Yaraku, Inc.

This file is part of Human Evaluation Tool.

Human Evaluation Tool is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

Human Evaluation Tool is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
Human Evaluation Tool. If not, see <https://www.gnu.org/licenses/>.

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, August 2023
"""

# User model.

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
