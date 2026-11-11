"""SPM-420 production monitoring API.

Scope: observation, records and reports. It has NO write path to the PLC; machine
control and every safety function stay in the PLC and the hard-wired circuits.
"""
import asyncio, hmac
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from . import collector
from .config import settings
from .db import Base, SessionLocal, engine, get_db
from .models import AlarmEvent, Batch, MaintenanceRecord, MaintenanceTask, Sample
from .schemas import AlarmOut, BatchIn, BatchOut, MaintenanceIn, MaintenanceOut
from .sources import MODE_NAMES, STATE_NAMES, make_source

hub = collector.Hub()

DEFAULT_TASKS = [
    ("Clean and inspect sealing jaws, PTFE cover", None, 1, "Brass brush only. Check serration damage and PTFE tape."),
    ("Inspect knife edge", 500_000, None, "Replace if seal cut is ragged."),
    ("Check pull-belt wear and tension", 1_000_000, 30, "Belts must be replaced as a pair."),
    ("Test emergency stops and guard interlocks", None, 7, "Functional test, record result."),
    ("Drain air filter / check regulator 0.6 MPa", None, 7, ""),
    ("Verify thermocouples against reference probe", None, 180, "Tolerance +/-3 K at 150 C."),
    ("Weigher calibration check with test weights", None, 30, "According to weigher supplier procedure."),
    ("Lubricate jaw guide bushings (H1 food-grade)", 2_000_000, 90, ""),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(func.count(MaintenanceTask.id))):
            db.add_all(MaintenanceTask(name=n, interval_cycles=c, interval_days=d, instructions=i) for n, c, d, i in DEFAULT_TASKS)
            db.commit()
    task = None
    source = make_source(settings)
    if source is not None:
        task = asyncio.create_task(collector.run(source, hub, SessionLocal, settings.poll_period_s, settings.sample_period_s))
    yield
    if task:
        task.cancel()


app = FastAPI(title="SPM-420 monitoring", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
                   allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])


def require_token(authorization: str = Header(default="")):
    """Bearer token for every endpoint that changes data."""
    if not settings.api_token:
        raise HTTPException(503, "write access disabled: API_TOKEN not configured")
    supplied = authorization.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(supplied.encode(), settings.api_token.encode()):
        raise HTTPException(401, "invalid token")


def _aware(dt):
    return dt if dt is None or dt.tzinfo else dt.replace(tzinfo=timezone.utc)


@app.get("/api/health")
def health():
    return {"status": "ok", "plc_source": settings.plc_source, "plc_online": bool(hub.latest and hub.latest.online)}


@app.get("/api/status")
def status():
    s = hub.latest
    if s is None:
        return {"online": False}
    d = s.model_dump()
    d["state_name"], d["mode_name"] = STATE_NAMES.get(s.state, "?"), MODE_NAMES.get(s.mode, "?")
    return d


@app.get("/api/production/summary")
def summary(hours: float = Query(8, gt=0, le=24 * 31), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = db.execute(select(Sample.ts, Sample.state, Sample.speed_bpm, Sample.bags_total)
                      .where(Sample.ts >= since).order_by(Sample.ts)).all()
    if len(rows) < 2:
        return {"hours": hours, "samples": len(rows), "bags": 0, "availability_pct": None, "mean_speed_bpm": None}
    running = [r for r in rows if r.state == 3]
    bags = max(0, rows[-1].bags_total - rows[0].bags_total)
    n_alarms = db.scalar(select(func.count(AlarmEvent.id)).where(AlarmEvent.raised_at >= since, AlarmEvent.alarm_class.in_(["A", "B"])))
    return {"hours": hours, "samples": len(rows), "bags": bags,
            "availability_pct": round(100 * len(running) / len(rows), 1),
            "mean_speed_bpm": round(sum(r.speed_bpm for r in running) / len(running), 1) if running else 0.0,
            "stops": n_alarms, "from": _aware(rows[0].ts), "to": _aware(rows[-1].ts)}


@app.get("/api/production/timeseries")
def timeseries(hours: float = Query(1, gt=0, le=72), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = db.scalars(select(Sample).where(Sample.ts >= since).order_by(Sample.ts).limit(30000)).all()
    step = max(1, len(rows) // 600)
    return [{"ts": _aware(r.ts), "speed_bpm": r.speed_bpm, "bags_total": r.bags_total, "state": r.state,
             "temps": [r.temp_z1, r.temp_z2, r.temp_z3]} for r in rows[::step]]


@app.get("/api/alarms", response_model=list[AlarmOut])
def alarms(active: bool = False, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    q = select(AlarmEvent).order_by(AlarmEvent.raised_at.desc()).limit(limit)
    if active:
        q = q.where(AlarmEvent.cleared_at.is_(None))
    return db.scalars(q).all()


@app.get("/api/alarms/pareto")
def alarm_pareto(hours: float = Query(24, gt=0, le=24 * 31), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    evs = db.scalars(select(AlarmEvent).where(AlarmEvent.raised_at >= since)).all()
    agg: dict[int, dict] = {}
    now = datetime.now(timezone.utc)
    for e in evs:
        a = agg.setdefault(e.alarm_id, {"alarm_id": e.alarm_id, "text": e.text, "class": e.alarm_class, "count": 0, "minutes": 0.0})
        a["count"] += 1
        a["minutes"] += ((_aware(e.cleared_at) or now) - _aware(e.raised_at)).total_seconds() / 60
    return sorted(({**a, "minutes": round(a["minutes"], 1)} for a in agg.values()), key=lambda a: -a["minutes"])


@app.get("/api/batches", response_model=list[BatchOut])
def list_batches(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    return db.scalars(select(Batch).order_by(Batch.id.desc()).limit(limit)).all()


@app.post("/api/batches", response_model=BatchOut, status_code=201, dependencies=[Depends(require_token)])
def open_batch(body: BatchIn, db: Session = Depends(get_db)):
    if db.scalar(select(Batch.id).where(Batch.closed_at.is_(None))):
        raise HTTPException(409, "another batch is still open")
    if db.scalar(select(Batch.id).where(Batch.batch_no == body.batch_no)):
        raise HTTPException(409, "batch number already exists")
    b = Batch(**body.model_dump(), bags_at_start=hub.latest.bags_total if hub.latest else 0)
    db.add(b); db.commit()
    return b


@app.post("/api/batches/{batch_id}/close", response_model=BatchOut, dependencies=[Depends(require_token)])
def close_batch(batch_id: int, db: Session = Depends(get_db)):
    b = db.get(Batch, batch_id)
    if b is None:
        raise HTTPException(404, "batch not found")
    if b.closed_at is not None:
        raise HTTPException(409, "batch already closed")
    b.closed_at = datetime.now(timezone.utc)
    b.bags_at_close = hub.latest.bags_total if hub.latest else b.bags_at_start
    db.commit()
    return b


@app.get("/api/batches/{batch_id}/report")
def batch_report(batch_id: int, db: Session = Depends(get_db)):
    b = db.get(Batch, batch_id)
    if b is None:
        raise HTTPException(404, "batch not found")
    evs = db.scalars(select(AlarmEvent).where(AlarmEvent.batch_id == batch_id).order_by(AlarmEvent.raised_at)).all()
    end_count = b.bags_at_close if b.bags_at_close is not None else (hub.latest.bags_total if hub.latest else b.bags_at_start)
    t = db.execute(select(func.min(Sample.temp_z1), func.max(Sample.temp_z1), func.min(Sample.temp_z2), func.max(Sample.temp_z2),
                          func.min(Sample.temp_z3), func.max(Sample.temp_z3)).where(Sample.batch_id == batch_id, Sample.state == 3)).one()
    return {"batch": BatchOut.model_validate(b), "bags_produced": max(0, end_count - b.bags_at_start),
            "nominal_output_kg": round(max(0, end_count - b.bags_at_start) * b.target_weight_g / 1000, 1),
            "seal_temperature_range_while_running": {"z1": [t[0], t[1]], "z2": [t[2], t[3]], "z3": [t[4], t[5]]},
            "alarms": [AlarmOut.model_validate(e) for e in evs],
            "note": "Weights are nominal (count x target). Actual weights come from the weigher/checkweigher records."}


@app.get("/api/maintenance/records", response_model=list[MaintenanceOut])
def maintenance_records(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    return db.scalars(select(MaintenanceRecord).order_by(MaintenanceRecord.done_at.desc()).limit(limit)).all()


@app.post("/api/maintenance/records", response_model=MaintenanceOut, status_code=201, dependencies=[Depends(require_token)])
def add_maintenance(body: MaintenanceIn, db: Session = Depends(get_db)):
    if body.task_id is not None and db.get(MaintenanceTask, body.task_id) is None:
        raise HTTPException(404, "task not found")
    r = MaintenanceRecord(**body.model_dump(), bags_total_at=hub.latest.bags_total if hub.latest else 0)
    db.add(r); db.commit()
    return r


@app.get("/api/maintenance/due")
def maintenance_due(db: Session = Depends(get_db)):
    """Maintenance report: each preventive task with cycles/days since last done."""
    now, bags = datetime.now(timezone.utc), (hub.latest.bags_total if hub.latest else 0)
    out = []
    for t in db.scalars(select(MaintenanceTask).where(MaintenanceTask.active)).all():
        last = db.scalar(select(MaintenanceRecord).where(MaintenanceRecord.task_id == t.id).order_by(MaintenanceRecord.done_at.desc()).limit(1))
        days = (now - _aware(last.done_at)).days if last else None
        cycles = bags - last.bags_total_at if last else bags
        due = (last is None) or (t.interval_days is not None and days >= t.interval_days) or \
              (t.interval_cycles is not None and cycles >= t.interval_cycles)
        out.append({"task_id": t.id, "name": t.name, "interval_cycles": t.interval_cycles, "interval_days": t.interval_days,
                    "last_done": _aware(last.done_at) if last else None, "days_since": days, "cycles_since": cycles, "due": due,
                    "instructions": t.instructions})
    return sorted(out, key=lambda x: not x["due"])


@app.websocket("/ws/live")
async def live(ws: WebSocket):
    await ws.accept()
    hub.clients.add(ws)
    try:
        if hub.latest:
            await ws.send_text(hub.latest.model_dump_json())
        while True:
            await ws.receive_text()          # clients send nothing meaningful; keeps the socket open
    except WebSocketDisconnect:
        pass
    finally:
        hub.clients.discard(ws)
