from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Snapshot(BaseModel):
    """What the collector reads from the PLC each poll (read-only)."""
    ts: datetime
    online: bool = True
    state: int = 0
    mode: int = 0
    speed_bpm: float = 0.0
    bags_total: int = 0
    bags_batch: int = 0
    empty_cycles: int = 0
    temps: list[float] = [0.0, 0.0, 0.0]
    temp_setpoints: list[float] = [0.0, 0.0, 0.0]
    active_alarms: list[int] = []
    recipe: str = ""


class BatchIn(BaseModel):
    batch_no: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9._\-/]+$")
    product: str = Field(min_length=1, max_length=60)
    target_weight_g: float = Field(gt=0, le=5000)
    planned_bags: int = Field(default=0, ge=0, le=10_000_000)
    film_lot: str = Field(default="", max_length=40)
    operator: str = Field(default="", max_length=40)
    notes: str = Field(default="", max_length=2000)


class BatchOut(ORM):
    id: int
    batch_no: str
    product: str
    target_weight_g: float
    planned_bags: int
    film_lot: str
    operator: str
    started_at: datetime
    closed_at: datetime | None
    bags_at_start: int
    bags_at_close: int | None
    notes: str


class AlarmOut(ORM):
    id: int
    alarm_id: int
    alarm_class: str
    text: str
    raised_at: datetime
    cleared_at: datetime | None
    batch_id: int | None


class MaintenanceIn(BaseModel):
    task_id: int | None = None
    done_by: str = Field(min_length=1, max_length=40)
    kind: str = Field(default="preventive", pattern="^(preventive|corrective)$")
    description: str = Field(default="", max_length=4000)
    downtime_min: float = Field(default=0, ge=0, le=100000)


class MaintenanceOut(ORM):
    id: int
    task_id: int | None
    done_at: datetime
    done_by: str
    bags_total_at: int
    kind: str
    description: str
    downtime_min: float
