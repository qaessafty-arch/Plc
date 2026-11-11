# 02 - Engineering specification (SPM-420 snack filling and packaging line)

Revision P1 - preliminary. Requirement IDs are referenced by the test plan. Status: R = requirement fixed for this project, A = assumption awaiting confirmation by the project owner.

## Scope

A line that takes loose fragile snack product from a floor hopper, weighs it, forms pillow bags from roll film, fills, seals, cuts and discharges them. Line = infeed hopper + Z-bucket elevator + 10-head multihead weigher on a platform + VFFS bagger (designed here) + take-off conveyor.

## Functional and performance requirements

| ID | Requirement | Value | Status |
|---|---|---|---|
| F-01 | Products | potato chips, extruded/crispy snacks, crackers, small biscuits, coated nuts and similar free-flowing pieces <= 70 mm | R |
| F-02 | Fill weight range | 20-500 g (weigher), reference 40 g chips | A |
| F-03 | Bag type | pillow bag, lap or fin seal; hole punch and gusset as later options | R |
| F-04 | Bag width | 80-200 mm (one forming set per width) | R |
| F-05 | Bag length | 80-300 mm, adjustable from HMI in 1 mm steps | R |
| F-06 | Film | heat-sealable laminates 30-80 µm (OPP/CPP, PET/VMPET/PE), max web 420 mm, roll OD 400 mm, core 76 mm | R |
| F-07 | Rated speed | 40 bags/min for the reference bag (160 x 230 mm, 40 g); adjustable 5-60 | A |
| F-08 | Weight accuracy | mean >= nominal; no bag below nominal minus the tolerable negative error of OIML R 87 (9 % at 40 g); target give-away <= 2 % | A |
| F-09 | Bag length accuracy | ±1 mm plain film; ±1 mm to print mark with registration | R |
| F-10 | Seal quality | hermetic (no leak in 30 s immersion/vacuum test), no product in seal | R |
| F-11 | Product breakage added by the line | <= 2 % by mass of pieces broken, reference chips (to be measured against a hand-packed control) | A |
| F-12 | Changeover | recipe change at HMI <= 1 min; forming-set change <= 15 min without special tools | R |
| F-13 | Recipes | >= 20 stored in the PLC | R |
| F-14 | Modes | automatic, manual, setup, maintenance | R |
| F-15 | "No product - no bag" | film is not pulled while the weigher has no charge | R |
| F-16 | Counters | total, batch (with target stop), shift | R |
| F-17 | Monitoring | optional PC system: status, statistics, batches, alarm history, maintenance - read-only towards the PLC | R |

## Site and utility requirements

| ID | Item | Value | Status |
|---|---|---|---|
| U-01 | Electrical supply | 3/N/PE AC 400/230 V 50 Hz TN-S, 16 A | A (Iraq: confirm voltage stability; ±10 % assumed, AVR/UPS for the control supply recommended) |
| U-02 | Connected load | 4.7 kW, running demand ~3.3 kW | calculated |
| U-03 | Compressed air | 0.6 MPa at the machine, 0.19 m³/min, dry, oil-free at point of use | calculated |
| U-04 | Ambient | 5-35 °C (40 °C with cabinet cooling), < 65 % RH (snacks are hygroscopic; the room, not the machine, protects the product) | A |
| U-05 | Floor | level ±5 mm over the footprint, >= 5 kN/m², free of vibration from other machinery | R |
| U-06 | Space | 6050 x 4100 mm floor, 4400 mm clear height | calculated |
| U-07 | Nitrogen (option) | food grade, 0.3 MPa, flow by trial | A |

## Design requirements

| ID | Requirement |
|---|---|
| D-01 | Product-contact parts: EN 1.4301 (304) or 1.4404 (316L), food-grade PP/PU/PTFE with declarations of compliance; Ra <= 0.8 µm where product slides; dimpled surfaces for oily chips |
| D-02 | Frame: stainless steel, closed sections sealed, no horizontal ledges above the product zone, hygienic feet |
| D-03 | No fall of product greater than 300 mm onto a hard surface without a deflector or slide (fragility) - except inside the fill tube, where the fall is unavoidable and the landing is on film/product |
| D-04 | Every hazardous movement inside interlocked guards; safety functions hard-wired or in a certified safety controller, PL d |
| D-05 | Modular: weigher, elevator, forming set, jaw cartridge, pull-belt units and cabinet replaceable without cutting or welding |
| D-06 | All parameters in engineering units on the HMI; no hidden potentiometers except air regulators and sensor teach buttons |
| D-07 | Lockable isolation of electricity and air; residual energy dissipated or indicated |
| D-08 | Documentation in English (Arabic operator instructions to be added for the Iraqi market) |

## Out of scope in this revision

Gusset and quad-seal attachments, continuous-motion (D-cam) jaws, checkweigher and metal detector integration logic, legal metrology approval, CE/Iraqi conformity assessment, detail (shop) drawings with tolerances for every machined part.
