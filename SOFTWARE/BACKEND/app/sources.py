"""PLC data sources. BOTH ARE READ-ONLY BY DESIGN: this application never writes
to the controller, so it cannot influence real-time control or any safety function."""
import math, random
from datetime import datetime, timezone
from .schemas import Snapshot

STATE_NAMES = {0: "STOPPED", 1: "STARTING", 2: "READY", 3: "RUNNING", 4: "STOPPING", 5: "FAULT", 6: "E-STOP"}
MODE_NAMES = {0: "OFF", 1: "MANUAL", 2: "SETUP", 3: "AUTO", 4: "MAINTENANCE"}


class SimulatedSource:
    """Plausible data for development and demonstrations. Clearly not a machine."""
    name = "simulated"

    def __init__(self, seed=1):
        self.rng = random.Random(seed); self.t = 0.0; self.bags = 0.0; self.fault_until = -1.0; self.alarm = 0

    async def read(self) -> Snapshot:
        self.t += 1.0
        if self.t > self.fault_until and self.rng.random() < 0.004:
            self.fault_until = self.t + self.rng.randint(20, 90); self.alarm = self.rng.choice([4, 6, 22, 3])
        fault = self.t <= self.fault_until
        speed = 0.0 if fault else 40.0 + self.rng.uniform(-0.4, 0.4)
        self.bags += speed / 60.0
        temps = [150 + 2 * math.sin(self.t / 17) + self.rng.uniform(-0.5, 0.5),
                 150 + 2 * math.sin(self.t / 19 + 1) + self.rng.uniform(-0.5, 0.5),
                 140 + 1.5 * math.sin(self.t / 23 + 2) + self.rng.uniform(-0.5, 0.5)]
        return Snapshot(ts=datetime.now(timezone.utc), state=5 if fault else 3, mode=3, speed_bpm=round(speed, 1),
                        bags_total=int(self.bags), bags_batch=int(self.bags), temps=[round(x, 1) for x in temps],
                        temp_setpoints=[150, 150, 140], active_alarms=[self.alarm] if fault else [],
                        recipe="Potato chips 40 g (SIMULATED)")


class OpcUaSource:
    """Reads DB_Machine / DB_Alarms / DB_Recipe through the S7-1200 OPC UA server.

    Node ids follow the TIA Portal convention ns=3;s="DB"."Member". The PLC must have the
    OPC UA server activated with a runtime licence and these DBs marked "accessible from
    HMI/OPC UA" as READ-ONLY. Only read services are used here. Not yet tested against a PLC.
    """
    name = "opcua"
    NODES = {
        "state": 'ns=3;s="DB_Machine"."State"', "mode": 'ns=3;s="DB_Machine"."Mode"',
        "speed_bpm": 'ns=3;s="DB_Machine"."Cnt"."ActualSpeed_bpm"', "bags_total": 'ns=3;s="DB_Machine"."Cnt"."BagsTotal"',
        "bags_batch": 'ns=3;s="DB_Machine"."Cnt"."BagsBatch"', "empty_cycles": 'ns=3;s="DB_Machine"."Cnt"."EmptyCycles"',
        "t1": 'ns=3;s="DB_Machine"."Zone"[1]."Actual"', "t2": 'ns=3;s="DB_Machine"."Zone"[2]."Actual"',
        "t3": 'ns=3;s="DB_Machine"."Zone"[3]."Actual"', "s1": 'ns=3;s="DB_Machine"."Zone"[1]."Setpoint"',
        "s2": 'ns=3;s="DB_Machine"."Zone"[2]."Setpoint"', "s3": 'ns=3;s="DB_Machine"."Zone"[3]."Setpoint"',
        "w1": 'ns=3;s="DB_Alarms"."Word1"', "w2": 'ns=3;s="DB_Alarms"."Word2"', "recipe": 'ns=3;s="DB_Recipe"."Active"."Name"',
    }

    def __init__(self, url, user="", password=""):
        self.url, self.user, self.password, self.client = url, user, password, None

    async def _connect(self):
        from asyncua import Client          # imported lazily: optional dependency
        c = Client(self.url, timeout=4)
        if self.user:
            c.set_user(self.user); c.set_password(self.password)
        await c.connect()
        self.client, self.nodes = c, {k: c.get_node(v) for k, v in self.NODES.items()}

    async def read(self) -> Snapshot:
        now = datetime.now(timezone.utc)
        try:
            if self.client is None:
                await self._connect()
            keys = list(self.nodes)
            vals = dict(zip(keys, await self.client.read_values([self.nodes[k] for k in keys])))
        except Exception:
            self.client = None
            return Snapshot(ts=now, online=False)
        word = int(vals["w1"]) | (int(vals["w2"]) << 16)
        return Snapshot(ts=now, state=int(vals["state"]), mode=int(vals["mode"]), speed_bpm=float(vals["speed_bpm"]),
                        bags_total=int(vals["bags_total"]), bags_batch=int(vals["bags_batch"]),
                        empty_cycles=int(vals["empty_cycles"]), temps=[float(vals[k]) for k in ("t1", "t2", "t3")],
                        temp_setpoints=[float(vals[k]) for k in ("s1", "s2", "s3")],
                        active_alarms=[i + 1 for i in range(32) if word >> i & 1], recipe=str(vals["recipe"]))


def make_source(settings):
    if settings.plc_source == "opcua":
        return OpcUaSource(settings.opcua_url, settings.opcua_user, settings.opcua_password)
    if settings.plc_source == "simulated":
        return SimulatedSource()
    return None
