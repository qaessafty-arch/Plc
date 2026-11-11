# HMI specification - KTP700 Basic PN (7", 800 x 480, resistive touch)

`6AV2123-2GB03-0AX0` [verified data sheet: 800 x 480, PROFINET, 800 tags, 250 screens, 50 users, 50 recipes x 100 records, 256-entry alarm buffer, 24 V DC 0.23 A].

**Deliverables in this folder**

| File | Purpose |
|---|---|
| `HMI_SPECIFICATION.md` | This document: screen-by-screen build specification for WinCC Basic (TIA Portal) |
| `hmi_tags.csv` | Every HMI tag, PLC address, limits and required user level (58 of 800 tags) |
| `../PLC/alarms.csv` | Discrete alarm texts (trigger tags `Alarm_Word1/2`, bit = id-1) |
| `hmi_prototype.html` | Clickable 800 x 480 browser prototype of all 14 screens with a built-in tag simulator |

A WinCC project file (`.ap17`) is a proprietary binary that can only be produced inside TIA Portal, so it is not included. The prototype is the editable reference for layout and navigation; the CSVs import directly into the TIA tag and alarm editors.

## Design rules

* Layout grid: header 800 x 48 (state, mode, recipe, user, clock, STOP and RESET always visible), content 800 x 376, navigation bar 800 x 56.
* Touch targets >= 64 x 48 px; no control closer than 8 px to another (resistive panel, gloved hands).
* Colour carries meaning only together with text: green = running, amber = waiting/warning, red = fault, blue = operator action required (IEC 60073). Background stays neutral grey; red is never used for decoration.
* Every numeric input has PLC-side limits (column min/max in `hmi_tags.csv`) and the same limits in the HMI tag; the PLC clamps again (`FB_TempZone` limits the setpoint, recipe speed is paced in `FB_BagCycle`).
* Momentary manual buttons use "SetBitWhileKeyPressed"; they are additionally interlocked in the PLC (`ManualEnable`). **The HMI is not a safety device.** There is no software E-stop; the STOP button is a normal cycle stop.
* Languages: English and Arabic (RTL layouts as a second language set), switchable at Login.

## User groups

| Group | Level | May do |
|---|---|---|
| (logged out) | 0 | view everything, STOP |
| Operator | 1 | start/stop/reset, select recipe, speed, batch target, heaters on/off, counters shift reset |
| Setter | 2 | + edit recipes, weights, temperatures, timings, single cycle, film jog |
| Maintenance | 3 | + manual functions (with key switch S4), diagnostics forcing view, maintenance counters |
| Administrator | 9 | + users, temperature band, language, date/time, backup/restore, alarm buffer clear |

Auto-logoff after 10 min. Passwords are managed in the panel's user administration, never stored in the PLC.

## Screens

| # | Screen | Content | Main tags |
|---|---|---|---|
| 1 | Login | user list, password, language, software versions | panel user administration |
| 2 | Main dashboard | state banner, mode buttons (OFF/MANUAL/SETUP/AUTO/MAINT), START, speed actual/set, batch counter with target bar, three temperatures with in-band lamp, first-out alarm text | Machine_State, Mode_Request, Cmd_Start, Speed_Actual, Bags_Batch, Temp_Zx_Act, Alarm_FirstOut |
| 3 | Machine overview | synoptic: hopper, elevator, weigher, former, belts, jaws, take-off; each element coloured by state; live step text ("50 SEAL DWELL"); sensor lamps | Cycle_Step, DI/DQ bytes |
| 4 | Production settings | speed, knife delay, air blast, N2 flush, coder on/off; SETUP functions: single cycle, empty bag | Rcp_Speed, Rcp_KnifeDelay, Cmd_SingleCycle, Cmd_EmptyBag |
| 5 | Product configuration | recipe list (20), load / save / copy, name, bag length, bag width (shows required forming set and tube OD), registration mark on/off, window, offset | Rcp_* |
| 6 | Weight settings | target weight (information + value to be keyed at the weigher; sent automatically only if the weigher option "Modbus TCP" is fitted), dump lead (weigher dump request before the film pull, 0-800 ms); link text to weigher panel; latest checkweigher statistics if fitted | Rcp_TargetWeight, Rcp_DumpLead |
| 7 | Temperature settings | 3 zones: setpoint, actual, output %, in-band lamp, trend 30 min; heaters ON/OFF; seal time | Rcp_Temp_Zx, Temp_Zx_Act/Out, Heaters_On, Rcp_SealTime |
| 8 | Motor speed settings | film pull velocity and acceleration, elevator %, take-off %, calculated cycle time and theoretical bags/min for the entered values | Rcp_PullVel, Rcp_PullAcc, Rcp_ElevSpeed, Rcp_TakeoffSpeed |
| 9 | Production counter | total (not resettable), batch, shift, empty cycles, batch target, run/stop time, efficiency % | Bags_*, Batch_Target |
| 10 | Machine diagnostics | DI/DQ lamps with tag names, axis status, safety relay status, air pressure, cabinet temperature, PLC cycle time | DI/DQ bytes, status tags |
| 11 | Alarm history | alarm view (active + buffer 256), acknowledge, per-alarm help text = "recovery" column of alarms.csv | Alarm_Word1/2 |
| 12 | Maintenance | momentary manual functions, film jog, maintenance counters (jaw cycles, knife cycles, belt metres) with reset by Maintenance user | Man_* |
| 13 | Operator management | panel "User view" object | - |
| 14 | Administrator settings | date/time, language, brightness, temperature band, alarm buffer clear, backup to USB, IP settings (read only) | Rcp_TempBand |

Navigation: bottom bar with Dashboard / Overview / Product / Settings (opens 4, 6, 7, 8 as tabs) / Counter / Alarms / Service (10, 12) / Admin (13, 14). An active class A/B alarm shows a red bar across the header that jumps to screen 11 on touch.

## Communication

HMI <-> PLC: S7 HMI connection over PROFINET (same subnet 192.168.10.0/24 as the drive). PLC protection level "HMI access" with a connection password; PUT/GET disabled. Acquisition cycles are in `hmi_tags.csv`; only tags on the visible screen are polled (WinCC default), alarm words continuously.
