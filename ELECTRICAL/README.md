# Electrical design package

**Status: design-level documentation, not production schematics.** The diagrams here fix the
architecture, protection concept, device list, I/O allocation and terminal numbering. Before
any panel is built they must be redrawn in an ECAD tool (EPLAN, QElectroTech, SEE Electrical),
checked against each manufacturer's current manual (terminal names, fuse ratings, cable
lengths, EMC rules) and verified according to IEC 60204-1 clause 18. Terminal designations of
third-party devices quoted here follow the usual manufacturer convention but **must be
confirmed from the device manual** - they are marked (confirm).

| File | Content |
|---|---|
| `SCHEMATICS/01_architecture.md` | System architecture, network, HMI communication |
| `SCHEMATICS/02_power_distribution.md` | Single-line diagram, protection and cable sizing, earthing |
| `SCHEMATICS/03_safety_circuits.md` | E-stop, guard, STO, safe air, heater cut-out; performance level estimate |
| `SCHEMATICS/04_motor_and_heater_wiring.md` | Servo, VFDs, heaters |
| `SCHEMATICS/05_sensor_and_io_wiring.md` | Sensor wiring principles, weigher interface |
| `WIRING/cable_schedule.csv` | Every field cable: from, to, type, cores, length estimate |
| `WIRING/terminal_plan.csv` | Terminal strips X1...X21 |
| `PANEL/panel_layout.md` | Cabinet layout, heat balance, segregation |
| `BOM/bom.csv`, `BOM/budget.py` | Bill of materials and budget generator |
| `../AUTOMATION/PLC/io_map.csv` | PLC I/O mapping (single source) |

Load, current, protection and 24 V budget calculations: `DOCUMENTATION/ENGINEERING/03_ENGINEERING_CALCULATIONS.md` section 7.
