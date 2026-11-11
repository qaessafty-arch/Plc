"""Single source of truth for the SPM-420 snack packaging line.

Every calculation, CAD script, simulation and document generator imports this
module, so a change here propagates everywhere after `make all`.

STATUS KEY used in comments
  [REQ]  requirement chosen for this project (design input)
  [ASM]  engineering assumption - must be confirmed by measurement or supplier
  [VER]  taken from a manufacturer data sheet checked on 2026-11-11
  [DRV]  derived by DOCUMENTATION/ENGINEERING/engineering_calcs.py
All lengths mm, masses kg, times s unless stated otherwise.
"""
import math

MACHINE_NAME = "SPM-420"
REVISION = "P1 (preliminary - not released for manufacture)"

# ---------------------------------------------------------------- products
# bulk densities are literature-typical values [ASM]; measure on real product.
PRODUCTS = {
    # key: (label, target g, bulk density g/L, bag width, bag length, fragile 1-5)
    "chips_40":    ("Potato chips 40 g",        40.0,  60.0, 160, 230, 5),
    "puffs_30":    ("Extruded puffs 30 g",      30.0,  45.0, 160, 240, 3),
    "crackers_100": ("Crackers 100 g",         100.0, 250.0, 140, 200, 4),
    "biscuits_150": ("Mini biscuits 150 g",    150.0, 350.0, 140, 200, 4),
    "nuts_200":    ("Coated nuts / mix 200 g", 200.0, 600.0, 140, 190, 2),
}
REFERENCE_PRODUCT = "chips_40"

# ---------------------------------------------------------------- bag / film
FILM_WIDTH_MAX = 420            # [REQ] "420 class" bagger
FILM_WIDTH_MIN = 180            # [REQ]
BAG_WIDTH_RANGE = (80, 200)     # [DRV] from film width
BAG_LENGTH_RANGE = (80, 300)    # [REQ]
LAP_OVERLAP = 20                # [ASM] fin/lap seal allowance on film width
END_SEAL_WIDTH = 12             # [ASM] each transverse seal land
FILM_THICKNESS_UM = 50          # [ASM] OPP20/VMCPP30-type laminate
FILM_DENSITY = 910              # kg/m3 [ASM] polypropylene based
FILM_ROLL_OD_MAX = 400          # [REQ]
FILM_CORE_ID = 76               # [REQ] 3 inch core
MAX_FILL_RATIO = 0.65           # [ASM] product volume / max pillow volume

# ---------------------------------------------------------------- cycle
RATED_BPM = 40                  # [REQ] design point for reference product
SEAL_DWELL = 0.45               # [ASM] to be tuned on real film
JAW_STROKE_TIME = 0.15          # [ASM] pneumatic, each direction
SETTLE_TIME = 0.05
PULL_ACCEL = 6.0                # m/s2 [ASM] limited by film slip on belts
PULL_VMAX = 0.80                # m/s  [ASM]
KNIFE_TIME = 0.10

# ---------------------------------------------------------------- film pull
PULL_PULLEY_DIA = 60.0          # belt drive pulley pitch dia
PULL_GEAR_RATIO = 5.0           # planetary gearbox
PULL_FILM_DRAG_N = 60.0         # [ASM] collar + unwind drag, measure with spring scale
PULL_BELT_LEN = 250
SERVO_RATED_NM = 1.27           # [VER] SIMOTICS S-1FL6034-2AF21-1AA1
SERVO_RATED_RPM = 3000          # [VER]
SERVO_KW = 0.4                  # [VER]

# ---------------------------------------------------------------- sealing
JAW_LENGTH = 240                # covers 200 bag width + margin
JAW_SECTION = (30, 40)          # width x height of each steel jaw
SEAL_PRESSURE_MPA = 0.40        # [ASM] on seal land, laminate dependent
VSEAL_LENGTH = 320
VSEAL_LAND = 10
VSEAL_PRESSURE_MPA = 0.20       # [ASM]
AIR_PRESSURE_MPA = 0.60         # gauge, regulated
CYL_JAW = (63, 60)              # bore, stroke ISO 15552
CYL_VSEAL = (40, 30)
CYL_KNIFE = (25, 20)
ROD_DIA = {63: 20, 40: 16, 25: 10}
HEATERS_W = {"Z1 front jaw": 500, "Z2 rear jaw": 500, "Z3 vertical bar": 300}
SEAL_TEMP_DEFAULT = 150         # deg C [ASM]
SEAL_TEMP_MAX = 220             # deg C hard limit in PLC
AMBIENT = 25

# ---------------------------------------------------------------- weigher
WEIGHER_HEADS = 10
WEIGHER_HOPPER_L = 1.6          # typical market size (see reference analysis)
WEIGHER_MAX_WPM = 70            # supplier class figure [ASM until FAT]
WEIGHER_DIA = 1100
WEIGHER_HEIGHT = 1250
WEIGHER_MASS = 380              # [ASM]
WEIGHER_KW = 1.5                # [ASM]

# ---------------------------------------------------------------- elevator
ELEV_BUCKET_L = 1.8
ELEV_BUCKET_PITCH = 152.4       # 6 inch chain attachment pitch
ELEV_FILL = 0.6                 # fragile product: do not heap [ASM]
ELEV_SPEED = 0.20               # m/s chain speed, low to protect chips
ELEV_KW = 0.37
TAKEOFF_KW = 0.18
FEEDER_KW = 0.10

# ---------------------------------------------------------------- geometry (CAD)
# Origin: floor level, on the forming-tube axis. X right, Y to rear, Z up.
BAGGER_W, BAGGER_D, BAGGER_H = 1000, 1300, 1500
BAGGER_FRONT_Y = -350           # front face of bagger frame
TUBE_TOP_Z = 1450
JAW_Z = 700
BELT_Z0 = 800
FUNNEL_TOP_Z = 1700
PLATFORM_Z = 2000
PLATFORM_SIZE = 1900
HANDRAIL_H = 1100
WEIGHER_BASE_Z = 2150
ELEV_INFEED_X = -2900
ELEV_WIDTH = 500
TAKEOFF_LEN = 1800
TAKEOFF_WIDTH = 300
CABINET = (300, 600, 1000)      # X thickness, Y width, Z height
FRAME_TUBE = 50
FRAME_WALL = 2.0

# ---------------------------------------------------------------- electrical
SUPPLY = "3/N/PE AC 400/230 V 50 Hz, TN-S"   # [ASM] Iraq/EU style supply
V_LN, V_LL = 230.0, 400.0
CONTROL_V = 24.0

# ---------------------------------------------------------------- economics
USD_TO_IQD = 1320               # CBI cash selling rate 2026 [VER]
TARIFF_USD_KWH = 0.10           # [ASM]
FILM_USD_KG = 3.5               # [ASM]
SHIFT_H = 8


def tube_diameter(bag_w: float) -> float:
    """Forming tube OD so that tube circumference = 2 x flat bag width."""
    return 2.0 * bag_w / math.pi


def film_width(bag_w: float) -> float:
    return 2.0 * bag_w + LAP_OVERLAP


def pillow_volume_l(w: float, h: float) -> float:
    """Max volume of a pillow made of two w x h rectangles (Robin's
    'paper bag' approximation), litres. h is the unsealed length."""
    w, h = (w, h) if h >= w else (h, w)
    v = w ** 3 * (h / (math.pi * w) - 0.142 * (1 - 10 ** (-h / w)))
    return v / 1e6
