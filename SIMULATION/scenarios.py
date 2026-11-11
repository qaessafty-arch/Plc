"""Closed-loop scenarios: Python PLC port + plant model. Used by run_simulation.py
and test_scenarios.py. Every scenario returns a dict with measured quantities and
a list of (check description, bool)."""
import statistics
from plc_model import Plc, Recipe, Inputs
from plant_model import Plant

DT = 0.002


class Rig:
    def __init__(self, recipe=None, seed=1, hot=True, target=None):
        self.r = recipe or Recipe()
        self.plc, self.plant, self.i = Plc(self.r), Plant(self.r, seed=seed, hot=hot, target=target), Inputs()
        self.trace = []; self.record = False; self.max_temp = 0.0

    def run(self, seconds, until=None):
        n = int(seconds / DT)
        for _ in range(n):
            self.plant.sensors(self.i)
            q = dict(self.plc.scan(self.i, DT))
            if not (self.i.EstopOk and self.i.GuardOk):      # hard-wired safety: safe 24 V bus + STO off
                q.update(JawClose=False, VSeal=False, Knife=False, PullCmd=False)
                self.plant.move_left = 0.0; self.plant.vel = 0.0
            self.plant.estop_drop = not self.i.EstopOk
            self.plant.step(q, DT)
            self.max_temp = max(self.max_temp, *self.plant.temp)
            if self.record:
                p = self.plant
                self.trace.append((p.t, self.plc.cyc.Step, p.jaw.x, p.vseal.x, p.knife.x, p.vel, q["DumpReq"],
                                   len(p.packets) > 0, self.i.BagOut, p.acc))
            self.i.PbStart = self.i.PbReset = False
            if until and until(self):
                return True
        return False

    def start_auto(self):
        self.i.ModeRequest = 3; self.i.HeatersOn = True
        self.run(0.5); self.i.PbStart = True; self.run(0.1)

    def reset(self):
        self.i.PbReset = True; self.run(0.05)

    def active(self):
        return [k for k in range(1, 33) if self.plc.alm.Active[k]]

    def good_bags(self):
        return [b for b in self.plant.bags if b["weight"] > 1.0]


def wstats(bags, target):
    w = [b["weight"] for b in bags]
    if len(w) < 2: return {}
    return dict(n=len(w), mean=round(statistics.fmean(w), 2), sd=round(statistics.pstdev(w), 2),
                min=round(min(w), 2), max=round(max(w), 2),
                within_10pct=round(100 * sum(abs(x - target) <= 0.1 * target for x in w) / len(w), 1))


def s01_normal(seconds=120):
    g = Rig(); g.start_auto(); g.run(3.0); g.record = True; g.run(4.5); g.record = False; g.run(seconds - 8)
    bags = g.good_bags(); p = g.plant
    ts = [b["t"] for b in p.bags]; per = [b - a for a, b in zip(ts[5:], ts[6:])]
    L = [b["length"] for b in p.bags[2:]]
    res = dict(sim_seconds=seconds, bags_plc=g.plc.bags, bags_plant_filled=len(bags), empty_plc=g.plc.empties,
               mean_period_s=round(statistics.fmean(per), 3), speed_bpm=round(60 / statistics.fmean(per), 1),
               plc_reported_speed_bpm=round(g.plc.speed, 1),
               weights=wstats(bags, 40.0), bag_length_mm=[round(min(L), 1), round(max(L), 1)],
               product_in_seal_events=p.in_seal, pieces_landed_jaws_closed=p.land_closed,
               pieces_landed_jaws_open=p.land_open, alarms=g.active(), state=g.plc.mode.State)
    checks = [("PLC bag count equals filled bags in plant (+/-1 in flight)", abs(g.plc.bags - len(bags)) <= 1),
              ("no product caught in the seal", p.in_seal == 0),
              ("every piece lands while the jaws are closed and support the new seal", p.land_open == 0 and p.land_closed > 0),
              ("all filled bags within +/-10 % of target", res["weights"]["within_10pct"] == 100.0),
              ("speed is paced to the 40 bags/min recipe value (+/-0.5)", abs(res["speed_bpm"] - 40.0) <= 0.5),
              ("speed reported by the PLC matches the real speed (+/-0.5)", abs(res["plc_reported_speed_bpm"] - res["speed_bpm"]) <= 0.5),
              ("bag length 230 +/-1 mm", abs(min(L) - 230) <= 1 and abs(max(L) - 230) <= 1),
              ("no alarm (warnings 21/26/32 allowed)", all(a in (21, 26, 32) for a in g.active())),
              ("exactly one empty leader bag", g.plc.empties == 1)]
    return res, checks, g


def s02_warmup():
    g = Rig(hot=False); g.i.ModeRequest = 3; g.i.HeatersOn = True; g.run(0.5); g.i.PbStart = True
    ok = g.run(900, until=lambda r: r.plc.mode.State == 3); t_ready = g.plant.t
    g.run(60)
    res = dict(time_to_running_min=round(t_ready / 60, 1), peak_temp_C=round(g.max_temp, 1),
               setpoints=list(g.r.TempSet), bags_after_60s=g.plc.bags)
    return res, [("reaches RUNNING without alarm 16", ok and 16 not in g.active()),
                 ("overshoot below 15 K", g.max_temp < max(g.r.TempSet) + 15),
                 ("no bag made before temperatures in band", all(b["t"] >= t_ready for b in g.plant.bags))], g


def s03_empty_hopper():
    g = Rig(); g.start_auto(); g.run(10); n0 = len(g.plant.bags); g.plant.product_supply = False
    g.run(20); n1 = len(g.plant.bags); film1 = g.plant.pos; al = g.active(); amber = g.plc.q["Amber"]
    g.run(5); film2 = g.plant.pos
    g.plant.product_supply = True; g.run(10)
    res = dict(bags_before=n0, bags_during_starvation=n1 - n0, alarms_during=al, amber_lamp=amber,
               film_wasted_mm=round(film2 - film1, 1), bags_after_refill=len(g.plant.bags) - n1, state=g.plc.mode.State)
    return res, [("starved warning 21 raised", 21 in al), ("machine waits: no film pulled while starved", film2 == film1),
                 ("stays in RUNNING (no fault)", g.plc.mode.State == 3), ("resumes by itself after refill", len(g.plant.bags) - n1 > 3),
                 ("no empty bags produced while starved", g.plc.empties == 1)], g


def s04_film_out():
    g = Rig(); g.plant.film_left_m = 3.0; g.start_auto(); g.run(40)
    st = g.plc.mode.State; al = g.active(); step = g.plc.cyc.Step
    last = g.plant.bags[-1] if g.plant.bags else {}
    g.plant.film_left_m = 500; g.reset(); st2 = g.plc.mode.State
    res = dict(alarms=al, state_after=st, cycle_step=step, jaws_open=g.plant.jaw.home, state_after_reset=st2,
               bags=len(g.plant.bags), charged_open_bag=g.plc.cyc.charged)
    return res, [("alarm 4 film end", 4 in al), ("machine stopped (STOPPED)", st == 0), ("jaws open, cycle idle", g.plant.jaw.home and step == 0),
                 ("reset returns to STOPPED, no automatic restart", st2 == 0 and g.plc.cyc.Step == 0)], g


def s05_wrong_weight():
    g = Rig(); g.start_auto(); g.run(10); g.plant.weight_bias = -8.0; g.run(20)
    late = [b for b in g.good_bags() if b["t"] > 13]
    res = dict(weights_after_bias=wstats(late, 40.0), alarms=g.active(), state=g.plc.mode.State)
    return res, [("FINDING: bagger PLC cannot see weight errors (no alarm, still RUNNING)", g.plc.mode.State == 3 and not g.plc.alm.AnyA and not g.plc.alm.AnyB),
                 ("bags are under weight in the plant", res["weights_after_bias"]["mean"] < 36)], g


def s06_jam():
    g = Rig(); g.start_auto(); g.run(10); g.plant.bag_jam = True; t0 = g.plant.t; n0 = len(g.plant.bags)
    g.run(10); al = g.active(); st = g.plc.mode.State; extra = len(g.plant.bags) - n0
    g2 = Rig(); g2.start_auto(); g2.run(10); g2.plant.conveyor_ok = False; g2.run(0.2)
    res = dict(bag_jam_alarms=al, state=st, bags_made_into_jam=extra, jaws_open=g.plant.jaw.home,
               conveyor_overload_alarms=g2.active(), conveyor_state=g2.plc.mode.State, conveyor_reaction_s=0.2)
    return res, [("alarm 22 bag jam", 22 in al), ("stops within 3 bags of the jam", extra <= 3), ("FAULT state, jaws open", st == 5 and g.plant.jaw.home),
                 ("take-off overload -> alarm 25 and FAULT within 0.2 s", 25 in g2.active() and g2.plc.mode.State == 5)], g


def s07_servo_fault():
    g = Rig(); g.start_auto(); g.run(10); g.plant.servo_fault = True; g.run(2)
    al = g.active(); st = g.plc.mode.State
    g.plant.servo_fault = False; g.plant.axis_error = False; g.reset(); g.run(1)
    res = dict(alarms=al, state=st, jaws_open=g.plant.jaw.home, state_after_reset=g.plc.mode.State, bags_after_reset=len(g.plant.bags))
    n = len(g.plant.bags); g.run(3)
    return res, [("alarm 18 or 19", 18 in al or 19 in al), ("FAULT, jaws open", st == 5 and g.plant.jaw.home),
                 ("after reset: STOPPED and no motion until START", g.plc.mode.State == 0 and len(g.plant.bags) == n)], g


def s08_overtemp():
    g = Rig(); g.start_auto(); g.run(10); g.plant.ssr_short[0] = True
    g.run(600, until=lambda r: 10 in r.active()); t_al = g.plant.t; g.run(120)
    res = dict(alarm_time_after_short_s=round(t_al - 10.6, 1), alarms=g.active(), peak_temp_C=round(g.max_temp, 1),
               heater_contactor=g.plant.heater_cont, independent_cutout_tripped=not g.plant.cutout_ok, state=g.plc.mode.State)
    return res, [("alarm 10 over-temperature", 10 in g.active()), ("heater contactor dropped", not g.plant.heater_cont),
                 (f"peak stays below cut-out {250} C", g.max_temp < 250), ("machine in FAULT", g.plc.mode.State == 5)], g


def s09_sensor_failure():
    g = Rig(); g.start_auto(); g.run(10); g.plant.tc_break[1] = True; g.run(1)
    a1 = g.active(); st1 = g.plc.mode.State; out = g.plc.zone[1].out
    g2 = Rig(); g2.start_auto(); g2.run(10)
    g2.run(5, until=lambda r: r.plant.jaw.home and r.plc.cyc.Step in (20, 30)); g2.plant.jaw.stuck = True; g2.run(3)
    a2 = g2.active(); st2 = g2.plc.mode.State
    g2.plant.jaw.stuck = False; g2.reset()
    res = dict(tc_break_alarms=a1, tc_state=st1, zone2_output_pct=out, jaw_stuck_alarms=a2, jaw_state=st2,
               valves_off=not g2.plc.q["JawClose"], alarms_after_single_reset=g2.active(), state_after_single_reset=g2.plc.mode.State)
    return res, [("thermocouple break -> alarm 14, zone output 0 %", 14 in a1 and out == 0.0), ("FAULT on TC break", st1 == 5),
                 ("jaw not closing -> alarm 6 and FAULT", 6 in a2 and st2 == 5), ("valves de-energised", not g2.plc.q["JawClose"]),
              ("one RESET press clears alarm and returns to STOPPED", 6 not in g2.active() and g2.plc.mode.State == 0)], g


def s10_power_loss():
    g = Rig(); g.start_auto(); g.run(10.3); n = len(g.plant.bags)
    g.plc.startup()                                    # controller restarts; inputs keep old HMI selections cleared
    g.i.ModeRequest = 0; g.i.HeatersOn = False; g.i.PbStart = False
    g.run(5); al = g.active(); st = g.plc.mode.State; made = len(g.plant.bags) - n
    g.i.ModeRequest = 3; g.i.HeatersOn = True; g.reset(); g.run(1); idle = len(g.plant.bags) - n
    g.i.PbStart = True; g.run(15)
    res = dict(alarms_after_restart=al, state_after_restart=st, bags_made_without_start=made, jaws_open=g.plant.jaw.home,
               bags_before_start_pressed=idle, bags_after_restart=len(g.plant.bags) - n)
    return res, [("alarm 30 power restart", 30 in al), ("no automatic restart", made <= 1 and st == 0 and idle <= 1),
                 ("production resumes only after RESET + START", len(g.plant.bags) - n > 3)], g


def s11_estop():
    g = Rig(); g.start_auto(); g.run(10)
    g.run(5, until=lambda r: r.plc.cyc.Step == 50 and r.plc.cyc.tStep > 0.1)      # mid seal
    g.i.EstopOk = False; g.run(DT * 2); q1 = dict(g.plc.q); st = g.plc.mode.State
    g.run(1.0); open_ = g.plant.jaw.home; heat = g.plant.heater_cont; n = len(g.plant.bags)
    g.i.EstopOk = True; g.run(3); st_rel = g.plc.mode.State; moved = len(g.plant.bags) - n
    g.reset(); st_reset = g.plc.mode.State; g.run(3); moved2 = len(g.plant.bags) - n
    g.i.PbStart = True; g.run(10)
    res = dict(outputs_one_scan_after=dict(JawClose=q1["JawClose"], Knife=q1["Knife"], HeaterCont=q1["HeaterCont"]),
               state=st, jaws_open_after_1s=open_, heaters_off=not heat, state_after_release=st_rel,
               state_after_reset=st_reset, bags_after_start=len(g.plant.bags) - n)
    return res, [("PLC outputs off within 2 scans (hardware is faster and independent)", not q1["JawClose"] and not q1["Knife"] and not q1["HeaterCont"]),
                 ("state ESTOP", st == 6), ("jaws open, heaters off", open_ and not heat),
                 ("releasing the button does not restart", st_rel == 6 and moved == 0),
                 ("reset alone does not restart", st_reset == 0 and moved2 == 0), ("START resumes production", len(g.plant.bags) - n > 2)], g


def s12_air_guard():
    g = Rig(); g.start_auto(); g.run(10); g.plant.air = False; g.run(2); a = g.active(); st = g.plc.mode.State
    g2 = Rig(); g2.start_auto(); g2.run(10); g2.i.GuardOk = False; g2.run(1)
    res = dict(air_alarms=a, air_state=st, guard_alarms=g2.active(), guard_state=g2.plc.mode.State,
               guard_heaters_kept=g2.plant.heater_cont, guard_jaws_open=g2.plant.jaw.home)
    return res, [("air loss -> alarm 3, FAULT", 3 in a and st == 5), ("guard open -> alarm 2, FAULT, jaws open", 2 in g2.active() and g2.plc.mode.State == 5 and g2.plant.jaw.home),
                 ("heaters stay on with guard open (hot-surface hazard handled by guarding/labels)", g2.plant.heater_cont)], g


SCENARIOS = [("S01 normal automatic production", s01_normal), ("S02 cold start / warm-up", s02_warmup),
             ("S03 empty product hopper", s03_empty_hopper), ("S04 missing packaging film", s04_film_out),
             ("S05 incorrect product weight", s05_wrong_weight), ("S06 jammed discharge / conveyor overload", s06_jam),
             ("S07 film-pull servo fault", s07_servo_fault), ("S08 excessive sealing temperature (SSR short)", s08_overtemp),
             ("S09 sensor failure (thermocouple, jaw sensor)", s09_sensor_failure), ("S10 power interruption", s10_power_loss),
             ("S11 emergency stop during sealing", s11_estop), ("S12 air loss / guard door", s12_air_guard)]
