import asyncio, logging
from datetime import datetime, timezone
from sqlalchemy import select
from .alarm_texts import describe
from .models import AlarmEvent, Batch, Sample
from .schemas import Snapshot

log = logging.getLogger("collector")


class Hub:
    """Keeps the latest snapshot and fans it out to WebSocket clients."""
    def __init__(self):
        self.latest: Snapshot | None = None
        self.clients: set = set()

    async def publish(self, snap: Snapshot):
        self.latest = snap
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send_text(snap.model_dump_json())
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.clients.discard(ws)


def open_batch_id(db):
    return db.scalar(select(Batch.id).where(Batch.closed_at.is_(None)).order_by(Batch.id.desc()).limit(1))


def process_snapshot(db, snap: Snapshot, prev_alarms: set, store_sample: bool) -> set:
    """Persist alarm transitions and (optionally) a sample. Returns the new active set."""
    now = snap.ts
    if not snap.online:
        return prev_alarms
    batch = open_batch_id(db)
    current = set(snap.active_alarms)
    for a in current - prev_alarms:
        cls, text = describe(a)
        db.add(AlarmEvent(alarm_id=a, alarm_class=cls, text=text, raised_at=now, batch_id=batch))
    for a in prev_alarms - current:
        ev = db.scalar(select(AlarmEvent).where(AlarmEvent.alarm_id == a, AlarmEvent.cleared_at.is_(None))
                       .order_by(AlarmEvent.id.desc()).limit(1))
        if ev:
            ev.cleared_at = now
    if store_sample:
        db.add(Sample(ts=now, state=snap.state, mode=snap.mode, speed_bpm=snap.speed_bpm, bags_total=snap.bags_total,
                      empty_cycles=snap.empty_cycles, temp_z1=snap.temps[0], temp_z2=snap.temps[1],
                      temp_z3=snap.temps[2], recipe=snap.recipe[:32], batch_id=batch))
    db.commit()
    return current


async def run(source, hub: Hub, session_factory, poll_s: float, sample_s: float):
    prev: set = set()
    with session_factory() as db:           # alarms still open from a previous run
        prev = set(db.scalars(select(AlarmEvent.alarm_id).where(AlarmEvent.cleared_at.is_(None))))
    last_sample = 0.0
    loop = asyncio.get_event_loop()
    while True:
        try:
            snap = await source.read()
            store = loop.time() - last_sample >= sample_s
            with session_factory() as db:
                prev = process_snapshot(db, snap, prev, store)
            if store:
                last_sample = loop.time()
            await hub.publish(snap)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("collector cycle failed")
        await asyncio.sleep(poll_s)
