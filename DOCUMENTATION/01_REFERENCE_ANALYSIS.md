# 01 - Reference machine analysis

Reference: <https://youtu.be/BCQ6pwSIyH4> - "Crispy snack chips biscuits filling machine, automatic machine for snack packaging" (YouTube Short, 13 s, channel *Grain Packing Line*, uploaded 2026-09-22).

## 1. What could and could not be examined

| Source | Access in this project | What it gives |
|---|---|---|
| Video title, channel, length, description | read | product class (chips, biscuits, crispy snacks); publisher is Samfull (Foshan), a maker of VFFS, premade-pouch and flow-wrap machines and end-of-line systems |
| **Video frames and audio** | **not accessible** - the build environment blocks video and thumbnail hosts | nothing. No frame of the video was viewed. |
| Publisher's product pages | read (samfull.net snack VFFS page) | machine family, published parameters of a comparable model |
| Other makers' published data | read (search results, data sheets) | typical parameters of the machine class |

**Consequence:** every statement below about the *specific machine in the video* is an inference from its title and its publisher's catalogue, not an observation. The title says "filling machine", which for this publisher can mean (a) a multihead weigher filling a VFFS bagger, (b) a weigher filling a premade-pouch machine, or (c) a weigher/counting filler for trays, jars or cans. The project owner's brief asks for film roll, forming collar, vertical and horizontal sealing and cutting, so the design follows interpretation (a), which is also the most common snack configuration. **Action for the project owner:** watch the 13 s clip against the checklist in section 4 and correct this file; if the clip shows a tray/jar filler, sections 2-8 of the project still apply but the bagger is replaced by a container indexing conveyor.

## 2. Operating principle of the machine class (weigher + VFFS)

1. Bulk product is tipped into a floor hopper; a vibratory feeder meters it into a Z-bucket elevator.
2. The elevator lifts it ~3.5 m and drops it onto the top cone of a multihead (combination) weigher.
3. Radial vibratory feeders move product to 10-14 feed hoppers, then weigh hoppers on load cells.
4. The weigher computer picks the combination of hoppers closest to (and not below) the target and discharges it down a collating chute.
5. Meanwhile the bagger pulls flat film from a roll over a forming collar into a tube around the fill tube, seals the longitudinal seam (vertical seal), and closes heated jaws across the tube: one stroke seals the top of the bag below, seals the bottom of the bag above and cuts between them.
6. The charge falls through the fill tube into the new bag; the cut bag drops onto a take-off conveyor.
7. A PLC synchronises "bag ready" with "charge ready".

## 3. The ten requested identifications

| # | Item | Inference for the reference | Basis | Confirmed from video? |
|---|---|---|---|---|
| 1 | Operating principle | gravimetric combination weighing + (probably) vertical form-fill-seal, intermittent motion | title + publisher catalogue | no |
| 2 | Product feeding | Z-type bucket elevator with vibratory infeed hopper | publisher lists "Bucket Elevator / Z-type Conveyor, Vibratory Feeder" as front-end for this line | no |
| 3 | Measuring / dispensing | multihead weigher, 10 or 14 heads, 1.6 L or 2.5 L hoppers, dimpled plates for snacks | publisher's "Multihead Weigher Packing Machine" family; market data: 10-head 1.6 L, 15-1000 g, up to ~70 weighments/min, ±0.5-2 g | no |
| 4 | Film mechanism | rear-mounted roll, dancer/tension rollers, eye-mark sensor, servo-driven double pull belts | publisher feature list: "Servo motor film drawing... Double belt film drawing... color code control" | no |
| 5 | Bag forming | forming collar + tube (format part per bag width); pillow, gusset, hanging-hole bags | publisher feature list | no |
| 6 | Vertical seal | heated bar against the forming tube, pneumatic, independent temperature control | "independent temperature control system" | no |
| 7 | Horizontal seal | pair of heated serrated jaws, pneumatic (standard models) or servo (high-speed models) | class standard; publisher speeds 80-150 bags/min imply servo jaws on the high-speed model | no |
| 8 | Cutting | zig-zag knife inside the jaw, pneumatically fired | class standard | no |
| 9 | Discharge | inclined take-off conveyor, optional checkweigher / metal detector | publisher option list | no |
| 10 | Control | PLC + colour touch screen with recipe memory and fault display; weigher has its own controller and touch screen | publisher feature list | no |

Hidden even in a good video (must not be guessed): drive brands, PLC type, heater power, load-cell capacity, jaw mechanism, safety category, software.

## 4. Checklist for viewing the clip (to close the open items)

- [ ] Is there a film roll and a forming collar (VFFS), or are premade pouches / trays / jars filled?
- [ ] Number of weigher heads (count the radial feeders).
- [ ] Bag style (pillow, gusset) and approximate bag width versus the jaw length.
- [ ] Jaw motion: pure open/close (intermittent, pneumatic) or D-motion following the film (continuous, servo)?
- [ ] Visible cycle rate: count bags in 10 s.
- [ ] Elevator type (Z-bucket, inclined belt) and where the operator loads product.
- [ ] Guarding: interlocked doors around the jaws?

## 5. Published reference data used for sanity checks

| Source (public page, read 2026-11-11) | Data |
|---|---|
| Samfull "Granule Snacks Food High Speed VFFS Machine", model SF-2.0GT | bags L 100-400 x W 80-250 mm; 80-150 bags/min; 20-500 g; film PET/VMPET/PE; air 0.65 m³/min; 3 kW; 1080 x 1300 x 1400 mm; 304 stainless frame |
| Spack "VFFS-420" | bag width 80-200 mm, length 100-250 mm, 10-60 bags/min, 300 kg |
| Generic 420-class listings | max film width 420 mm, bag 60-200 x 60-300 mm, 5-60 bags/min, ~4 kW, air 0.65 MPa |
| High Dream 10-head basic weigher (manufacturer post) | 15-1000 g, min. scale ±0.5-2 g, max 70 weighments/min, hopper 1.6 L / 3 L |
| Vtops VFFS family | machine sizes 1170 x 820 x 1290 to 1320 x 950 x 1360 mm, 350-550 kg |

These are advertised values. They are used only to check that the design figures of this project are in a realistic range (they are: SPM-420 bagger 1000 x 1300 x 1500 mm frame, 40 bags/min rated, 4.7 kW connected for the whole line, 0.19 m³/min air).

## 6. Design decision taken from the analysis

Design the **intermittent-motion, 420 mm class VFFS bagger in full**, and treat the **multihead weigher and Z-elevator as specified, purchased modules** with defined mechanical and electrical interfaces. Reason: a combination weigher is a legally relevant measuring instrument whose value lies in its load-cell electronics, feeder tuning and approvals; rebuilding one is a separate multi-year product. The combination algorithm itself is nevertheless provided and tested (`AUTOMATION/WEIGHER_CONTROLLER`, `SIMULATION/weigher_sim.py`) for the educational configuration.
