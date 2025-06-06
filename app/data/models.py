from datetime import datetime

from sqlalchemy import String, ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    candidates: Mapped[list["Candidate"]] = relationship(back_populates="category")
    is_active: Mapped[int] = mapped_column(default=0)

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    votes: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="candidates")
    received_votes: Mapped[list["Vote"]] = relationship(back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("user_id", "candidate_id", name="uq_user_candidate"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    candidate: Mapped["Candidate"] = relationship(back_populates="received_votes")


class Channel(Base):
    __tablename__ = 'channels'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    chat_id: Mapped[int] = mapped_column()
