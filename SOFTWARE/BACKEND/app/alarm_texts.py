"""Alarm id -> (class, text). Loaded from AUTOMATION/PLC/alarms.csv when available so
that PLC, HMI and monitoring use one list; falls back to generic text otherwise."""
import csv, os

_PATHS = [os.environ.get("ALARMS_CSV", ""),
          os.path.join(os.path.dirname(__file__), "..", "alarms.csv"),
          os.path.join(os.path.dirname(__file__), "..", "..", "..", "AUTOMATION", "PLC", "alarms.csv")]


def load():
    for p in _PATHS:
        if p and os.path.exists(p):
            with open(p, newline="") as f:
                return {int(r["id"]): (r["class"], r["text"]) for r in csv.DictReader(f)}
    return {}


ALARMS = load()


def describe(alarm_id: int):
    return ALARMS.get(alarm_id, ("?", f"Alarm {alarm_id}"))
