from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def utcnow():
    return datetime.now(timezone.utc)


class Sample(Base):
    """Periodic machine snapshot (default every 10 s)."""
    __tablename__ = "samples"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    state: Mapped[int] = mapped_column(Integer)
    mode: Mapped[int] = mapped_column(Integer)
    speed_bpm: Mapped[float] = mapped_column(Float)
    bags_total: Mapped[int] = mapped_column(Integer)
    empty_cycles: Mapped[int] = mapped_column(Integer, default=0)
    temp_z1: Mapped[float] = mapped_column(Float)
    temp_z2: Mapped[float] = mapped_column(Float)
    temp_z3: Mapped[float] = mapped_column(Float)
    recipe: Mapped[str] = mapped_column(String(32), default="")
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("batches.id"), nullable=True)


class AlarmEvent(Base):
    __tablename__ = "alarm_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alarm_id: Mapped[int] = mapped_column(Integer, index=True)
    alarm_class: Mapped[str] = mapped_column(String(1))
    text: Mapped[str] = mapped_column(String(120))
    raised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("batches.id"), nullable=True)
    __table_args__ = (Index("ix_alarm_open", "alarm_id", "cleared_at"),)


class Batch(Base):
    __tablename__ = "batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_no: Mapped[str] = mapped_column(String(40), unique=True)
    product: Mapped[str] = mapped_column(String(60))
    target_weight_g: Mapped[float] = mapped_column(Float)
    planned_bags: Mapped[int] = mapped_column(Integer, default=0)
    film_lot: Mapped[str] = mapped_column(String(40), default="")
    operator: Mapped[str] = mapped_column(String(40), default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    bags_at_start: Mapped[int] = mapped_column(Integer, default=0)
    bags_at_close: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class MaintenanceTask(Base):
    """Preventive task with an interval in machine cycles and/or days."""
    __tablename__ = "maintenance_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    interval_cycles: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("maintenance_tasks.id"), nullable=True)
    done_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    done_by: Mapped[str] = mapped_column(String(40))
    bags_total_at: Mapped[int] = mapped_column(Integer, default=0)
    kind: Mapped[str] = mapped_column(String(20), default="preventive")   # preventive | corrective
    description: Mapped[str] = mapped_column(Text, default="")
    downtime_min: Mapped[float] = mapped_column(Float, default=0.0)
