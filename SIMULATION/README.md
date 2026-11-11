# Simulation

```
pip install matplotlib pytest
python3 SIMULATION/weigher_sim.py       # Monte-Carlo combination weighing -> weigher_results.json
python3 SIMULATION/run_simulation.py    # 12 closed-loop scenarios -> RESULTS.md, results.json, timing_diagram.png
python3 -m pytest SIMULATION -q         # same scenarios as assertions
```

| File | Role |
|---|---|
| `plc_model.py` | hand port of the SCL blocks (same step numbers and names) |
| `plant_model.py` | cylinders, servo profile, thermal zones, weigher, falling product, bag formation |
| `scenarios.py` | normal run, warm-up and ten abnormal scenarios |
| `weigher_sim.py` | combination weigher statistics |

These are model results. They test the sequence design against stated assumptions; they are not measurements of a machine and they do not prove the SCL source compiles.
