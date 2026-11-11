# Weigher controller reference code

The industrial and semi-industrial configurations buy the multihead weigher as a
complete, legally verifiable unit with its own controller; the bagger PLC talks to it
through four hard-wired signals (ready, dump request, dump done, no-fault) plus enable.

For the **educational prototype** (and for anyone building their own weigher) this folder
holds the one algorithm that matters: choosing the head combination. `combination.c`
is portable C99 without heap or floating point, exhaustive over all subsets using a
Gray-code walk.

Status: compiled with gcc and tested on a PC against a brute-force reference
(20 000 random cases, see `test_combination.c`). **Not run on a microcontroller, no
load-cell front end, no legal-for-trade approval.** A real weigher additionally needs:
per-head filtering and stability detection, zero tracking, feeder amplitude control per
head, staggered dump timing, and calibration with certified weights.

Suggested hardware for a self-built 4-10 head unit (not built, not verified): one 24-bit
bridge ADC per head (HX711 class for the prototype, AD7190/ADS1232 class for better
speed and noise), single-point load cells 0.6-3 kg C3, stepper-driven hopper gates,
an STM32-class MCU, RS-485/Modbus RTU or dry contacts to the PLC.
