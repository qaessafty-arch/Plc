# 06 - Product and packaging configuration

## Adjustable parameters and where they live

| Parameter | Range | Set at | Mechanism |
|---|---|---|---|
| Product weight | 20-500 g | weigher panel (HMI shows/stores the value) | combination target |
| Filling quantity per head | automatic | weigher | feeder amplitude/time per recipe |
| Bag width | 80-200 mm | mechanical | change forming set (one per width); move pull belts and registration sensor |
| Bag length | 80-300 mm | HMI recipe | servo index length (or print mark) |
| Production speed | 5-60 bags/min | HMI recipe | cycle pacing in `FB_BagCycle` |
| Conveyor / elevator speed | 10-100 % | HMI recipe | VFD reference |
| Sealing temperature | 60-210 °C per zone | HMI recipe | PI control |
| Sealing time | 150-2000 ms | HMI recipe | dwell step |
| Knife delay, dump advance, air blast, N2 | see `hmi_tags.csv` | HMI recipe | timers |

## Starting recipes (all values are starting points for trials, not validated settings)

| Product | Target g | Bag W x L | Tube OD | Film web | Fill ratio | Speed | Temps Z1/Z2/Z3 | Seal ms | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Potato chips | 40 | 160 x 230 | 101.9 | 340 | 0.59 | 40 | 150/150/140 | 450 | most fragile; lowest feeder amplitudes; N2 recommended |
| Extruded puffs | 30 | 160 x 240 | 101.9 | 340 | 0.55 | 45 | 150/150/140 | 400 | very light (45 g/L): air blast off, longest product string |
| Crackers | 100 | 140 x 200 | 89.1 | 300 | 0.55 | 40 | 150/150/140 | 450 | sharp corners: thicker film or lower drop |
| Mini biscuits | 150 | 140 x 200 | 89.1 | 300 | 0.59 | 35 | 155/155/145 | 500 | crumbs in seal: fit crumb catcher on weigher |
| Coated nuts / mix | 200 | 140 x 190 | 89.1 | 300 | 0.50 | 35 | 155/155/145 | 500 | dense: check bag drop impact on bottom seal while hot |

Fill ratio = product bulk volume / maximum pillow volume, limit 0.65; values from the calculation sheet. Bulk densities are literature-typical assumptions: **measure each product** (1 L cylinder, loose fill, 5 repeats) before fixing a bag size.

## Why products cannot share settings

| Property | Effect | Parameter that must change |
|---|---|---|
| Bulk density 45-600 g/L | bag volume, string length in the tube | bag size, speed, dump advance |
| Piece mass 0.2-8 g | weighing resolution | number of heads per dump, feeder tuning |
| Fragility | breakage | amplitudes, drop heights, speed |
| Oil/seasoning/crumbs | seal contamination, sticking | dimple plates, seal temperature/time, cleaning interval |
| Film structure and thickness | seal window | temperature, dwell, pressure |
| Piece size vs tube ID | bridging | forming set size (tube ID >= 1.5 x largest piece) |

Changeover procedure: `MANUFACTURING/assembly_instructions.md` section "Format change".
