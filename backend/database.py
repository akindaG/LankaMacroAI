import os
from pathlib import Path

from sqlalchemy import JSON, ForeignKey, Numeric, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "var").mkdir(exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'var/lankamacro.db'}")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    metadata_json: Mapped[dict] = mapped_column(JSON)


class Observation(Base):
    __tablename__ = "observations"
    period: Mapped[str] = mapped_column(String(7), primary_key=True)
    series: Mapped[str] = mapped_column(String(30), primary_key=True)
    value: Mapped[float] = mapped_column(Numeric(12, 4))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    metadata_json: Mapped[dict] = mapped_column(JSON)


def session():
    with Session(engine) as db:
        yield db
