# Regenerates every derived artefact from machine_params.py
.PHONY: all calcs cad drawings sim budget test
all: calcs cad drawings sim budget test
calcs:
	python3 DOCUMENTATION/ENGINEERING/engineering_calcs.py > /dev/null
cad:
	python3 CAD/SCRIPTS/build_cad.py
drawings:
	python3 CAD/SCRIPTS/build_drawings.py
sim:
	python3 SIMULATION/weigher_sim.py > /dev/null
	python3 SIMULATION/run_simulation.py
budget:
	python3 ELECTRICAL/BOM/budget.py > /dev/null
test:
	python3 -m pytest SIMULATION -q
	cd SOFTWARE/BACKEND && python3 -m pytest -q
	gcc -std=c99 -Wall -Wextra -O2 AUTOMATION/WEIGHER_CONTROLLER/combination.c AUTOMATION/WEIGHER_CONTROLLER/test_combination.c -o /tmp/test_combination && /tmp/test_combination
