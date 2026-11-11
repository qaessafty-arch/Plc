from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from app import collector
from app.db import SessionLocal
from app.main import app, hub
from app.schemas import Snapshot

AUTH = {"Authorization": "Bearer test-token"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def snap(t, bags, alarms=(), state=3, online=True):
    return Snapshot(ts=t, online=online, state=state, mode=3, speed_bpm=40.0 if state == 3 else 0.0, bags_total=bags,
                    temps=[150, 151, 140], temp_setpoints=[150, 150, 140], active_alarms=list(alarms), recipe="chips")


def feed(snaps):
    prev = set()
    with SessionLocal() as db:
        for s in snaps:
            prev = collector.process_snapshot(db, s, prev, True)
            hub.latest = s
    return prev


def test_health_and_empty_status(client):
    assert client.get("/api/health").json()["status"] == "ok"
    hub.latest = None
    assert client.get("/api/status").json() == {"online": False}


def test_write_requires_token(client):
    body = dict(batch_no="B-1", product="chips", target_weight_g=40)
    assert client.post("/api/batches", json=body).status_code == 401
    assert client.post("/api/batches", json=body, headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_validation_rejects_bad_input(client):
    assert client.post("/api/batches", json=dict(batch_no="x;drop", product="p", target_weight_g=40), headers=AUTH).status_code == 422
    assert client.post("/api/batches", json=dict(batch_no="B-9", product="p", target_weight_g=-1), headers=AUTH).status_code == 422


def test_batch_lifecycle_alarms_and_report(client):
    t0 = datetime.now(timezone.utc) - timedelta(minutes=10)
    feed([snap(t0, 1000)])
    r = client.post("/api/batches", json=dict(batch_no="B-2026-001", product="Potato chips", target_weight_g=40, planned_bags=500), headers=AUTH)
    assert r.status_code == 201 and r.json()["bags_at_start"] == 1000
    bid = r.json()["id"]
    assert client.post("/api/batches", json=dict(batch_no="B-2", product="p", target_weight_g=40), headers=AUTH).status_code == 409
    feed([snap(t0 + timedelta(minutes=1), 1040), snap(t0 + timedelta(minutes=2), 1080, alarms=[4], state=5),
          snap(t0 + timedelta(minutes=4), 1080, alarms=[], state=3), snap(t0 + timedelta(minutes=5), 1120)])
    al = client.get("/api/alarms").json()
    assert len(al) == 1 and al[0]["alarm_id"] == 4 and al[0]["cleared_at"] is not None and al[0]["batch_id"] == bid
    assert "Film" in al[0]["text"]                      # text comes from AUTOMATION/PLC/alarms.csv
    assert client.get("/api/alarms?active=true").json() == []
    par = client.get("/api/alarms/pareto?hours=1").json()
    assert par[0]["alarm_id"] == 4 and 1.9 <= par[0]["minutes"] <= 2.1
    assert client.post(f"/api/batches/{bid}/close", headers=AUTH).status_code == 200
    assert client.post(f"/api/batches/{bid}/close", headers=AUTH).status_code == 409
    rep = client.get(f"/api/batches/{bid}/report").json()
    assert rep["bags_produced"] == 120 and rep["nominal_output_kg"] == 4.8 and len(rep["alarms"]) == 1
    assert client.get("/api/batches/9999/report").status_code == 404


def test_summary_and_timeseries(client):
    s = client.get("/api/production/summary?hours=1").json()
    assert s["bags"] == 120 and s["availability_pct"] == 80.0 and s["mean_speed_bpm"] == 40.0 and s["stops"] == 1
    assert len(client.get("/api/production/timeseries?hours=1").json()) == 5


def test_offline_snapshot_changes_nothing(client):
    before = len(client.get("/api/alarms").json())
    with SessionLocal() as db:
        out = collector.process_snapshot(db, snap(datetime.now(timezone.utc), 0, online=False), {4}, True)
    assert out == {4} and len(client.get("/api/alarms").json()) == before


def test_maintenance(client):
    due = client.get("/api/maintenance/due").json()
    assert len(due) >= 5 and all(d["due"] for d in due)          # nothing recorded yet
    tid = due[0]["task_id"]
    assert client.post("/api/maintenance/records", json=dict(task_id=tid, done_by="tech")).status_code == 401
    assert client.post("/api/maintenance/records", json=dict(task_id=99999, done_by="tech"), headers=AUTH).status_code == 404
    r = client.post("/api/maintenance/records", json=dict(task_id=tid, done_by="tech", description="done", downtime_min=12), headers=AUTH)
    assert r.status_code == 201 and r.json()["bags_total_at"] == 1120
    d = {x["task_id"]: x for x in client.get("/api/maintenance/due").json()}
    assert d[tid]["due"] is False and d[tid]["cycles_since"] == 0


def test_websocket_pushes_latest(client):
    with client.websocket_connect("/ws/live") as ws:
        assert '"bags_total":1120' in ws.receive_text()
