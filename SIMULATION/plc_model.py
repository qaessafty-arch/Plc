"""Python port of the SCL blocks in AUTOMATION/PLC (same step numbers, same names).

Purpose: exercise the SEQUENCE DESIGN against a plant model before any hardware
exists. It is a hand port, not a compiled copy of the SCL, so a pass here does
not prove the SCL text is free of errors.
"""
from dataclasses import dataclass, field

CLASS = [1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 3, 2, 1, 2, 1, 3, 1, 2, 3, 2, 1, 3]


@dataclass
class Recipe:
    BagLength_mm: float = 230.0
    PullVelocity_mm_s: float = 800.0
    PullAccel_mm_s2: float = 6000.0
    SealTime_ms: int = 450
    TempSet: tuple = (150.0, 150.0, 140.0)
    TempBand: float = 8.0
    KnifeDelay_ms: int = 200
    KnifeTime_ms: int = 100
    DumpLead_ms: int = 55
    SettleTime_ms: int = 50
    SpeedSet_bpm: float = 40.0
    UseRegMark: bool = False
    BatchTarget: int = 0


class TON:
    def __init__(self): self.et = 0.0; self.q = False
    def __call__(self, IN, pt, dt):
        self.et = min(self.et + dt, pt) if IN else 0.0
        self.q = IN and self.et >= pt
        return self.q


class RTrig:
    def __init__(self): self.old = False; self.q = False
    def __call__(self, clk):
        self.q = clk and not self.old; self.old = clk; return self.q


class TempZone:
    """FB_TempZone - called every 100 ms."""
    def __init__(self, kp=4.0, ti=60.0, max_temp=220.0):
        self.kp, self.ti, self.max = kp, ti, max_temp
        self.integ = self.phase = self.out = 0.0
        self.actual = 25.0; self.in_band = self.over = self.brk = False; self.ssr = False

    def __call__(self, enable, raw, setpoint, band, ct=0.1):
        self.brk = raw >= 32767 or raw <= -2000
        if not self.brk:
            self.actual = raw / 10.0
        sp = max(0.0, min(setpoint, self.max - 10.0))
        self.over = self.actual > self.max
        self.in_band = (not self.brk) and abs(self.actual - sp) <= band
        if enable and not self.brk and not self.over:
            err = sp - self.actual
            out = self.kp * err + self.integ
            if (0.0 < out < 100.0) or (out >= 100.0 and err < 0) or (out <= 0.0 and err > 0):
                self.integ += self.kp * err * ct / self.ti
            self.integ = max(0.0, min(self.integ, 100.0))
            self.out = max(0.0, min(self.kp * err + self.integ, 100.0))
        else:
            self.out = 0.0; self.integ = 0.0
        self.phase += ct
        if self.phase >= 1.0 - 1e-9:
            self.phase = 0.0
        self.ssr = enable and self.phase < self.out / 100.0
        return self.ssr


class BagCycle:
    """FB_BagCycle."""
    T_ACT = 0.6

    def __init__(self):
        self.Step = 0; self.stepOld = 0; self.tStep = 0.0; self.tCycle = 0.0
        self.qJawClose = self.qVSeal = self.qKnife = self.qDumpRequest = self.qPullExecute = False
        self.Waiting = self.BagDone = self.EmptyDone = False
        self.ToJawClose = self.ToJawOpen = self.ToVSeal = self.ToKnife = self.BagJam = False
        self.charged = self.dumpIssued = self.bagExpected = self.singleLatch = False
        self.missedBags = 0; self.CycleTime_ms = 0
        self.dumpCmd = False; self.dumpAt = 0.0; self.dumpPulseT = 0.0

    def __call__(self, dt, r: Recipe, Run, SingleCycle, NoProduct, Abort, CycleStop, Reset, TempsInBand,
                 FilmPresent, AirOk, WeigherReady, JawClosed, JawOpen, VSealBack, KnifeHome, PullDone,
                 PullError, BagOutEdge):
        self.BagDone = self.EmptyDone = False
        self.dumpCmd = False
        period = 60.0 / max(r.SpeedSet_bpm, 1.0)
        self.ToJawClose = self.ToJawOpen = self.ToVSeal = self.ToKnife = self.BagJam = False
        if SingleCycle:
            self.singleLatch = True
        if Abort and self.Step != 900:
            self.Step = 900
        if BagOutEdge:
            self.bagExpected = False; self.missedBags = 0
        s = self.Step
        et = self.tStep
        if s == 0:
            self.Waiting = False; self.qPullExecute = False
            if (Run or self.singleLatch) and not CycleStop:
                self.Step = 10
        elif s == 10:
            ready = TempsInBand and FilmPresent and AirOk and JawOpen and VSealBack and KnifeHome
            want = ((Run and not CycleStop) or self.singleLatch) and not NoProduct
            if self.dumpIssued:
                self.Waiting = False
                if self.tCycle >= max(period, self.dumpAt + r.DumpLead_ms / 1000) - 1e-9:
                    self.Step = 20
            elif CycleStop or not (Run or self.singleLatch):
                self.Waiting = False
                self.Step = 20 if (self.charged and TempsInBand and FilmPresent and AirOk) else 0
            elif want:
                self.Waiting = not (TempsInBand and WeigherReady)
                if ready and WeigherReady and (self.tCycle + r.DumpLead_ms / 1000 >= period - 1e-9 or self.singleLatch):
                    self.dumpIssued = True; self.dumpCmd = True; self.dumpAt = self.tCycle
            else:
                self.Waiting = not TempsInBand
                if ready and (self.tCycle >= period - 1e-9 or self.singleLatch):
                    self.Step = 20
        elif s == 20:
            self.Waiting = False; self.qPullExecute = True
            if PullError:
                self.qPullExecute = False; self.Step = 900
            elif PullDone:
                self.qPullExecute = False; self.Step = 30
        elif s == 30:
            if et >= r.SettleTime_ms / 1000:
                self.Step = 40
        elif s == 40:
            self.qJawClose = True; self.qVSeal = True
            if JawClosed:
                self.Step = 50
            elif et >= self.T_ACT:
                self.ToJawClose = True; self.Step = 900
        elif s == 50:
            self.qKnife = r.KnifeDelay_ms / 1000 <= et < (r.KnifeDelay_ms + r.KnifeTime_ms) / 1000
            if et >= r.SealTime_ms / 1000:
                self.qKnife = False; self.Step = 60
        elif s == 60:
            self.qJawClose = self.qVSeal = self.qKnife = False
            if JawOpen and VSealBack and KnifeHome:
                self.Step = 70
            elif et >= self.T_ACT:
                self.ToJawOpen = not JawOpen; self.ToVSeal = not VSealBack; self.ToKnife = not KnifeHome
                self.Step = 900
        elif s == 70:
            if self.charged: self.BagDone = True
            else: self.EmptyDone = True
            if self.bagExpected:
                self.missedBags += 1
            self.bagExpected = True
            self.BagJam = self.missedBags >= 2
            self.charged = self.dumpIssued; self.dumpIssued = False
            self.singleLatch = False
            self.Step = 900 if self.BagJam else 10
        elif s == 900:
            self.qJawClose = self.qVSeal = self.qKnife = self.qPullExecute = False
            self.dumpIssued = self.singleLatch = self.Waiting = False
            if Reset and not Abort:
                self.missedBags = 0; self.bagExpected = False; self.charged = False
                self.Step = 0
        # dump pulse (TP 100 ms) from the one-scan command; lead timer request -> pull
        if self.dumpCmd:
            self.dumpPulseT = 0.1
        self.qDumpRequest = self.dumpPulseT > 0
        self.dumpPulseT = max(0.0, self.dumpPulseT - dt)
        # timers
        self.tStep = self.tStep + dt if self.Step == self.stepOld else 0.0
        if self.Step == 20 and self.stepOld != 20:
            self.CycleTime_ms = int(round(self.tCycle * 1000))       # pull start to pull start
        self.tCycle = 0.0 if (self.Step == 20 and self.stepOld != 20) else self.tCycle + dt
        self.stepOld = self.Step


class ModeManager:
    """FB_ModeManager."""
    def __init__(self):
        self.Mode = 0; self.State = 0
        self.startEdge, self.resetEdge, self.tStarting = RTrig(), RTrig(), TON()
        self.RunCycle = self.CycleStop = self.Abort = self.MotionEnable = self.ManualEnable = False
        self.HeaterEnable = self.ResetPulse = False

    def __call__(self, dt, ModeRequest, PbStart, PbStop, PbReset, KeyMaint, EstopOk, GuardOk, AlarmA, AlarmB,
                 CycleStep, TempsInBand, AxisReady, BatchDone, HeatersOn, HeaterInhibit=False):
        self.startEdge(PbStart); self.resetEdge(PbReset); self.ResetPulse = self.resetEdge.q
        if self.State in (0, 2, 5) and CycleStep in (0, 900):
            if ModeRequest == 4 and not KeyMaint:
                pass
            elif 0 <= ModeRequest <= 4:
                self.Mode = ModeRequest
        if self.Mode == 4 and not KeyMaint:
            self.Mode = 0
        if not EstopOk:
            self.State = 6
        elif AlarmA or not GuardOk:
            if self.State != 6:
                self.State = 5
        if CycleStep == 900 and self.State in (3, 4):
            self.State = 5
        st = self.State
        if st == 0:
            if self.Mode == 3 and self.startEdge.q: self.State = 1
            elif self.Mode in (1, 2, 4): self.State = 2
        elif st == 1:
            if PbStop: self.State = 0
            elif AxisReady and TempsInBand: self.State = 3
            elif self.tStarting.q: self.State = 0
        elif st == 2:
            if self.Mode in (0, 3): self.State = 0
        elif st == 3:
            if PbStop or AlarmB or BatchDone: self.State = 4
        elif st == 4:
            if CycleStep == 0: self.State = 0
        elif st == 5:
            if self.resetEdge.q and not AlarmA and GuardOk and EstopOk: self.State = 0
        elif st == 6:
            if EstopOk and self.resetEdge.q:
                self.State = 5 if (AlarmA or not GuardOk) else 0
        self.tStarting(self.State == 1, 900.0, dt)
        self.Abort = self.State in (5, 6)
        self.RunCycle = self.State == 3
        self.CycleStop = self.State in (4, 0)
        self.MotionEnable = EstopOk and GuardOk and 1 <= self.State <= 4
        self.ManualEnable = EstopOk and GuardOk and self.State == 2 and self.Mode in (1, 4)
        self.HeaterEnable = HeatersOn and EstopOk and not HeaterInhibit and self.Mode != 0


class Alarms:
    """FB_Alarms."""
    def __init__(self):
        self.Active = [False] * 33; self.AnyA = self.AnyB = self.AnyC = False
        self.FirstOut = 0; self.history = []

    def __call__(self, cond, reset, t=0.0):
        self.AnyA = self.AnyB = self.AnyC = False
        for i in range(1, 33):
            c = CLASS[i - 1]
            if cond[i]:
                if not self.Active[i]:
                    self.history.append((round(t, 3), i))
                    if self.FirstOut == 0 and c < 3:
                        self.FirstOut = i
                self.Active[i] = True
            elif reset or c == 3:
                self.Active[i] = False
            if self.Active[i]:
                if c == 1: self.AnyA = True
                elif c == 2: self.AnyB = True
                else: self.AnyC = True
        if reset and not self.AnyA and not self.AnyB:
            self.FirstOut = 0


class FilmPull:
    """FB_FilmPull reduced to its handshake (the axis itself lives in the plant model)."""
    def __init__(self):
        self.step = 0; self.Done = self.Error = self.Busy = False; self.execOld = False; self.wd = TON()
        self.cmd_move = False

    def __call__(self, dt, Execute, Enable, axis_done, axis_error, Reset):
        self.cmd_move = False
        if self.step == 0:
            self.Busy = False
            if Execute and not self.execOld and Enable:
                self.Done = self.Error = False; self.step = 10; self.cmd_move = True
        elif self.step == 10:
            self.Busy = True
            if axis_done: self.step = 30
            elif axis_error or self.wd.q or not Enable: self.step = 90
        elif self.step == 30:
            self.Busy = False; self.Done = True
            if not Execute:
                self.Done = False; self.step = 0
        elif self.step == 90:
            self.Busy = False; self.Error = True
            if Reset or not Execute:
                self.Error = False; self.step = 0
        self.wd(self.step == 10, 3.0, dt)
        self.execOld = Execute


@dataclass
class Inputs:
    PbStart: bool = False; PbStop: bool = False; PbReset: bool = False; KeyMaint: bool = False
    EstopOk: bool = True; GuardOk: bool = True; AirOk: bool = True; FilmPresent: bool = True
    DancerHigh: bool = False; DancerLow: bool = True
    JawClosed: bool = False; JawOpen: bool = True; VSealBack: bool = True; KnifeHome: bool = True
    WghReady: bool = False; WghNoFault: bool = True; WghFeedReq: bool = False
    BagOut: bool = False; ChuteBlocked: bool = False; HopperLow: bool = False
    ElevVfdOk: bool = True; TakeoffVfdOk: bool = True; HeaterContFb: bool = False
    ThermCutoutOk: bool = True; DcFuseOk: bool = True
    TempRaw: list = field(default_factory=lambda: [250, 250, 250])
    AxisReady: bool = True; AxisDone: bool = False; AxisError: bool = False
    ModeRequest: int = 0; HeatersOn: bool = False; CmdSingle: bool = False; CmdEmpty: bool = False


class Plc:
    """OB1 + OB30 + OB100 of 20_OB_Main.scl."""
    def __init__(self, recipe=None):
        self.r = recipe or Recipe()
        self.mode, self.cyc, self.alm, self.pull = ModeManager(), BagCycle(), Alarms(), FilmPull()
        self.zone = [TempZone(), TempZone(), TempZone()]
        self.rBagOut, self.rReset = RTrig(), RTrig()
        self.tDancer, self.tStarved, self.tTempLow, self.tHeatCont, self.tTakeoff = TON(), TON(), TON(), TON(), TON()
        self.bags = self.empties = 0; self.speed = 0.0
        self.power_restart = False; self.was_running = False
        self.q = dict(JawClose=False, VSeal=False, Knife=False, DumpReq=False, UnwindRun=False, HeaterCont=False,
                      Ssr=[False] * 3, ElevRun=False, TakeoffRun=False, FeederRun=False, WghEnable=False,
                      Green=False, Amber=False, Red=False, PullCmd=False)
        self.t = 0.0; self._ob30 = 0.0

    def startup(self):                       # OB100
        was = self.was_running
        self.__init__(self.r)
        self.power_restart = was

    def scan(self, i: Inputs, dt):
        self.t += dt
        # ---- OB30 every 100 ms
        self._ob30 += dt
        if self._ob30 >= 0.1 - 1e-9:
            self._ob30 = 0.0
            en = self.mode.HeaterEnable and i.HeaterContFb
            for k in range(3):
                self.q["Ssr"][k] = self.zone[k](en, i.TempRaw[k], self.r.TempSet[k], self.r.TempBand)
        z = self.zone
        tempsOk = z[0].in_band and z[1].in_band and z[2].in_band
        running = self.mode.State in (3, 4)
        self.rBagOut(not i.BagOut)
        self.rReset(i.PbReset)
        if self.rReset.q:
            self.power_restart = False
        c = [False] * 33
        c[1] = not i.EstopOk
        c[2] = (not i.GuardOk) and i.EstopOk
        c[3] = not i.AirOk
        c[4] = not i.FilmPresent
        c[6], c[7], c[8], c[9] = self.cyc.ToJawClose, self.cyc.ToJawOpen, self.cyc.ToVSeal, self.cyc.ToKnife
        for k in range(3):
            c[10 + k] = z[k].over; c[13 + k] = z[k].brk
        c[16] = self.tTempLow(running and not tempsOk, 5.0, dt)
        c[17] = not i.ThermCutoutOk
        c[18] = self.mode.MotionEnable and i.AxisError
        c[19] = self.pull.Error
        c[20] = not i.WghNoFault
        c[21] = self.tStarved(self.cyc.Step == 10 and not i.WghReady and running, 10.0, dt)
        c[22] = self.cyc.BagJam
        c[23] = i.ChuteBlocked
        c[24] = not i.ElevVfdOk
        c[25] = not i.TakeoffVfdOk
        c[26] = i.HopperLow
        c[27] = not i.DcFuseOk
        c[28] = self.tDancer((i.DancerHigh and i.DancerLow) or (i.DancerHigh and not self.q["UnwindRun"] and running), 3.0, dt)
        c[30] = self.power_restart
        c[31] = self.tHeatCont(self.q["HeaterCont"] != i.HeaterContFb, 0.5, dt)
        c[32] = running and not tempsOk and not self.tTempLow.q
        self.alm(c, self.rReset.q, self.t)
        A = self.alm.Active
        inhibit = any(c[k] for k in (10, 11, 12, 13, 14, 15, 17, 27, 31)) or any(A[k] for k in (10, 11, 12, 17, 31))
        m = self.mode
        m(dt, i.ModeRequest, i.PbStart, i.PbStop, i.PbReset, i.KeyMaint, i.EstopOk, i.GuardOk, self.alm.AnyA,
          self.alm.AnyB, self.cyc.Step, tempsOk, i.AxisReady,
          self.r.BatchTarget > 0 and self.bags >= self.r.BatchTarget, i.HeatersOn, inhibit)
        self.was_running = m.State == 3
        self.pull(dt, self.cyc.qPullExecute, m.MotionEnable, i.AxisDone, i.AxisError, m.ResetPulse)
        self.q["PullCmd"] = self.pull.cmd_move
        self.cyc(dt, self.r, m.RunCycle, i.CmdSingle and m.Mode == 2 and m.State == 2, i.CmdEmpty and m.Mode == 2,
                 m.Abort, m.CycleStop and m.Mode != 2, m.ResetPulse, tempsOk, i.FilmPresent, i.AirOk,
                 i.WghReady and i.WghNoFault, i.JawClosed, i.JawOpen, i.VSealBack, i.KnifeHome,
                 self.pull.Done, self.pull.Error, self.rBagOut.q)
        q = self.q
        q["JawClose"], q["VSeal"] = self.cyc.qJawClose, self.cyc.qVSeal
        q["Knife"] = self.cyc.qKnife and i.JawClosed
        q["DumpReq"] = self.cyc.qDumpRequest
        q["WghEnable"] = running and not i.ChuteBlocked
        q["HeaterCont"] = m.HeaterEnable
        if i.DancerHigh and m.MotionEnable: q["UnwindRun"] = True
        elif i.DancerLow or not m.MotionEnable: q["UnwindRun"] = False
        self.tTakeoff(not running, 5.0, dt)                  # off-delay: runs 5 s after stop
        q["TakeoffRun"] = (running or (not self.tTakeoff.q and self.t > 5.0 and self.bags + self.empties > 0)) and i.TakeoffVfdOk
        q["ElevRun"] = running and i.WghFeedReq and i.ElevVfdOk and i.WghNoFault
        q["FeederRun"] = q["ElevRun"]
        if self.cyc.BagDone:
            self.bags += 1
            if self.cyc.CycleTime_ms > 0: self.speed = 60000.0 / self.cyc.CycleTime_ms
        if self.cyc.EmptyDone:
            self.empties += 1
        q["Green"] = m.State == 3 and not self.cyc.Waiting
        q["Amber"] = self.cyc.Waiting or self.alm.AnyC or m.State == 1
        q["Red"] = m.State >= 5
        return q
