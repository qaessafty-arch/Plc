# PLC program - Siemens S7-1200 (CPU 1215C DC/DC/DC), Structured Text (SCL)

**Status: source code, not yet compiled or downloaded.** No TIA Portal is available in
the environment that produced these files, so syntax errors are possible and the first
task at the bench is "import, compile, fix". The *logic* of `FB_BagCycle`,
`FB_ModeManager`, `FB_Alarms` and `FB_TempZone` has been exercised through the Python
port in `SIMULATION/plc_model.py` (see `SIMULATION/RESULTS.md`), which is evidence about
the sequence design, not about this source text.

| File | Content |
|---|---|
| `io_map.csv` | Every PLC address with device tag, signal type and safety note (source for the tag table) |
| `alarms.csv` | Alarm id, class, operator text, reaction, recovery |
| `01_Types.udt` | `UDT_Recipe`, `UDT_TempZone`, `UDT_Counters` |
| `02_DB_Global.db` | `DB_Recipe` (20 recipes, retentive), `DB_Machine`, `DB_Alarms` |
| `10_FB_TempZone.scl` | PI + time-proportioned SSR + sensor-break/over-temperature |
| `11_FB_FilmPull.scl` | Servo index, registration-mark retarget, jog |
| `12_FB_BagCycle.scl` | Form-fill-seal step sequence |
| `13_FB_ModeManager.scl` | Modes (OFF/MANUAL/SETUP/AUTO/MAINTENANCE) and states |
| `14_FB_Alarms.scl` | Alarm latching and classification |
| `20_OB_Main.scl` | OB1, OB30 (100 ms), OB40 (eye-mark), OB100 |

## Hardware configuration to create in TIA Portal (V17 or later)

1. CPU 1215C DC/DC/DC `6ES7215-1AG40-0XB0`; enable system clock memory (`Clock_1Hz` = M0.5).
2. Slot 2: SM 1223 16DI/16DO `6ES7223-1BL32-0XB0`, addresses I8.0/Q8.0.
3. Slot 3: SM 1231 AI4 x TC (order number to be confirmed against the current catalogue), type K, degC, address IW96, wire-break diagnostics on.
4. PROFINET: SINAMICS V90 PN (GSD/HSP), telegram 3; KTP700 Basic `6AV2123-2GB03-0AX0`.
5. Technology object `Axis_FilmPull`: positioning axis, PROFIdrive, unit mm, 37.699 mm per gearbox-output revolution (pi x 60 mm pulley / 5:1 gearbox -> 7.540 mm per motor rev), no homing required (relative moves), following-error monitoring on.
6. I0.0: hardware interrupt, rising edge -> OB40; input filter 0.1 ms.
7. Global tags `M_MarkSeen`, `M_MarkPosition`, `M_RegMissCount`, `M_PowerRestart`, `M_BuzzerAck`, timers `T_*` (TON_TIME) and edges `R_*` (R_TRIG) as global instance DBs.

Import: *External source files -> Add new external file* (all files), then *Generate blocks from source* in the order of the file numbers.

## What the PLC does NOT do

Emergency stop, guard-door monitoring, servo STO and the heater thermal cut-out are
hard-wired (see `ELECTRICAL/SCHEMATICS/03_safety_circuits.md`). The standard CPU only
reads their status for messages and sequencing. If a safety PLC is preferred (industrial
configuration), use CPU 1215FC with F-DI/F-DQ and keep the same sequence code.
