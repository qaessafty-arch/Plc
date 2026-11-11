"""Plant (physics) model for the SPM-420 bagger. All parameters are ASSUMPTIONS
taken from machine_params.py / engineering_calcs.py; none is measured."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import machine_params as P
from weigher_sim import MultiheadWeigher


class Cylinder:
    def __init__(self, t_travel): self.x = 0.0; self.t = t_travel; self.stuck = False
    def step(self, cmd, air, dt):
        if self.stuck: return
        v = dt / self.t
        self.x = min(1.0, self.x + v) if (cmd and air) else max(0.0, self.x - v)
    @property
    def out(self): return self.x >= 0.999
    @property
    def home(self): return self.x <= 0.001


class Plant:
    def __init__(self, recipe, seed=1, hot=True, target=None):
        ref = P.PRODUCTS[P.REFERENCE_PRODUCT]
        self.r = recipe
        self.rng = random.Random(seed)
        self.jaw, self.vseal, self.knife = Cylinder(0.12), Cylinder(0.08), Cylinder(0.04)
        self.air = True
        self.film_left_m = 2000.0; self.film_break = False
        self.pos = 0.0; self.vel = 0.0; self.move_left = 0.0; self.axis_done = False; self.axis_error = False
        self.servo_fault = False; self.belt_slip = 0.0
        t0 = [float(x) for x in recipe.TempSet] if hot else [25.0] * 3
        self.temp = list(t0); self.tc = list(t0)
        self.C = [1108.0, 1108.0, 583.0]; self.k = [0.9, 0.9, 0.7]; self.pw = [500.0, 500.0, 300.0]
        self.ssr_short = [False] * 3; self.tc_break = [False] * 3
        self.heater_cont = False; self.cutout_ok = True
        self.wg = MultiheadWeigher(target=target or ref[1], seed=seed)
        self.wg_period = 60.0 / P.WEIGHER_MAX_WPM
        self.wg_timer = 0.5; self.wg_ready = False; self.wg_next = None
        self.wg_fault = False; self.product_supply = True; self.weight_bias = 0.0
        self.t_lead = math.sqrt(2 * (P.WEIGHER_BASE_Z + 450 - P.JAW_Z) / 1000 / 9.81) + 0.08
        self.string = 0.35
        self.packets = []                       # (arrival time, grams)
        self.acc = 0.0; self.bags = []; self.in_seal = 0
        self.land_closed = 0; self.land_open = 0; self.land_rel = []   # where each piece landed (jaws closed / not)
        self.jaw_was_closed = False; self.cut_done = False
        self.bag_out_until = -1.0; self.bag_jam = False
        self.dump_old = False; self.t = 0.0; self.conveyor_ok = True; self.estop_drop = False
        self.dancer = 0.5; self.log = []

    # ---------------------------------------------------------------- step
    def step(self, q, dt):
        t = self.t = self.t + dt
        air = self.air
        self.jaw.step(q["JawClose"], air, dt); self.vseal.step(q["VSeal"], air, dt); self.knife.step(q["Knife"], air, dt)
        # --- servo axis: trapezoid, command edge loads one bag length
        if q["PullCmd"]:
            self.move_left = self.r.BagLength_mm; self.axis_done = False
        if self.servo_fault:
            self.axis_error = True; self.vel = 0.0
        elif self.move_left > 0:
            a, vmax = self.r.PullAccel_mm_s2, self.r.PullVelocity_mm_s
            v_stop = math.sqrt(2 * a * self.move_left)
            self.vel = min(self.vel + a * dt, vmax, v_stop)
            d = min(self.vel * dt, self.move_left)
            self.move_left -= d
            film = d * (1 - self.belt_slip)
            if not self.jaw.home:                      # film cannot move through closed jaws
                film = 0.0
            self.pos += film; self.film_left_m -= film / 1000
            self.dancer = min(1.0, self.dancer + film / 400)
            if self.move_left <= 1e-6:
                self.move_left = 0.0; self.vel = 0.0; self.axis_done = True
        if q["UnwindRun"]:
            self.dancer = max(0.0, self.dancer - 1.5 * dt)
        # --- heaters: first-order bar + thermocouple lag
        for k in range(3):
            on = (q["Ssr"][k] or self.ssr_short[k]) and self.heater_cont
            self.temp[k] += ((self.pw[k] if on else 0.0) - self.k[k] * (self.temp[k] - P.AMBIENT)) / self.C[k] * dt
            self.tc[k] += (self.temp[k] - self.tc[k]) / 3.0 * dt
        self.cutout_ok = self.cutout_ok and max(self.temp) < P.SEAL_TEMP_MAX + 30
        self.heater_cont = q["HeaterCont"] and self.cutout_ok and not self.estop_drop
        # --- weigher
        if not self.wg_ready and not self.wg_fault and q["WghEnable"] and self.product_supply:
            self.wg_timer -= dt
            if self.wg_timer <= 0:
                res = self.wg.cycle()
                if res: self.wg_next = res[0] + self.weight_bias; self.wg_ready = True
                else: self.wg_timer = self.wg_period
        if q["DumpReq"] and not self.dump_old and self.wg_ready:
            n = 12
            for j in range(n):
                self.packets.append((t + self.t_lead + self.string * j / (n - 1), self.wg_next / n))
            self.wg_ready = False; self.wg_timer = self.wg_period
        self.dump_old = q["DumpReq"]
        # --- product arrival at jaw plane
        rest = []
        for ta, g in self.packets:
            if ta <= t:
                if 0.05 < self.jaw.x < 0.999: self.in_seal += 1
                if self.jaw.out: self.land_closed += 1
                else: self.land_open += 1
                self.land_rel.append(ta)
                self.acc += g
            else: rest.append((ta, g))
        self.packets = rest
        # --- a bag is finished when the knife cuts with jaws closed
        if self.jaw.out and self.knife.out and not self.cut_done:
            self.cut_done = True
            self.bags.append(dict(t=round(t, 3), weight=round(self.acc_prev if hasattr(self, "acc_prev") else 0.0, 2),
                                  length=round(self.pos - getattr(self, "pos_prev", 0.0), 1),
                                  temp=[round(x, 1) for x in self.temp]))
            self.pos_prev = self.pos
            if not self.bag_jam: self.bag_out_until = t + 0.25 + 0.15
        if self.jaw.out and not self.jaw_was_closed:      # closing instant separates the bags
            self.acc_prev = self.acc; self.acc = 0.0
        if self.jaw.home: self.cut_done = False
        self.jaw_was_closed = self.jaw.out

    # ---------------------------------------------------------------- sensors
    def sensors(self, i):
        t = self.t
        i.AirOk = self.air
        i.FilmPresent = self.film_left_m > 0 and not self.film_break
        i.JawClosed, i.JawOpen = self.jaw.out, self.jaw.home
        i.VSealBack, i.KnifeHome = self.vseal.home, self.knife.home
        i.WghReady, i.WghNoFault = self.wg_ready, not self.wg_fault
        i.WghFeedReq = True
        i.BagOut = (self.bag_out_until - 0.15) <= t <= self.bag_out_until
        i.HeaterContFb = self.heater_cont
        i.ThermCutoutOk = self.cutout_ok
        i.TempRaw = [32767 if self.tc_break[k] else int(round(self.tc[k] * 10)) for k in range(3)]
        i.AxisDone, i.AxisError, i.AxisReady = self.axis_done, self.axis_error, not self.servo_fault
        i.DancerHigh, i.DancerLow = self.dancer > 0.8, self.dancer < 0.2
        i.TakeoffVfdOk = self.conveyor_ok
        return i
