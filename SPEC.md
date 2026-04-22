# Purfling Cutter — Design Spec (v0.2)

A 3D-printed jig that holds a Dremel rotary tool over a stringed-instrument
top so a cutter bit can rout a constant-distance channel from the edge,
following the body's perimeter via a bearing.

This document describes the **as-built** design in `cutter.py`. Constant
names below match constants in the source.

## Parts

Three printed parts plus a sourced bearing, an M4 bolt and an M4 hex nut.
Standoffs that connect shoe to plate are **not yet designed** and remain out
of scope here.

| Part            | Function                                                                 | Source                  |
|-----------------|--------------------------------------------------------------------------|-------------------------|
| `plate`         | Holds the Dremel via a 3/4"-12 UN internal thread.                       | `build_plate()`         |
| `shoe`          | Pill-shaped body raised above the work; small Ø surround boss at the front is the only contact patch. Houses the bit hole, the stadium-shaped bearing slot, and standoff bolt holes. | `build_shoe()`  |
| `upper_sleeve`  | Drops into the shoe slot from above; clamps the shoe; rides on bearing inner race. | `build_upper_sleeve()` |
| `lower_sleeve`  | Goes into the bearing bore from below; captures the bearing inner race.  | `build_lower_sleeve()`  |
| 608 bearing     | Edge follower (Ø22 OD × Ø8 bore × 7 mm).                                 | sourced                 |
| M4 bolt         | Clamps the sleeve stack from below into the upper sleeve's captive nut.   | sourced (M4 × ~25)      |
| M4 hex nut      | Captive in a hex pocket inside the upper sleeve top flange.              | sourced (7 mm AF × 3.2) |

## Coordinate system

Shoe-local frame is the world frame for the assembly.

- **+X**: long axis of the shoe (surround at +X end, standoffs at −X end).
- **+Y**: short axis (width).
- **+Z**: up. **z = 0 is the bottom of the surround boss**, which is the
  only part that touches the workpiece. The shoe body itself is raised to
  z = `SURROUND_HEIGHT` (= 4) and floats above the work.

The shoe is symmetric about the X-axis. The plate, in its own local frame,
lies in the XY plane (Z = 0 to PLATE_T); when assembled it is translated
upward by the (TBD) standoff height and laterally so its threaded bore
sits over the shoe's bit hole.

## Shoe layout

Three features lie on the shoe centerline (Y = 0), in this order along X:

```
TOP VIEW (+Z down):
+----------------------------------------------------+
|  o       o        [====slot====]        ( O )      |
+----------------------------------------------------+
   bolt#1  bolt#2     bearing channel       surround
   (back)              (upper sleeve         (bit hole)
                        stem slides;
                        M4 bolt from below)

SIDE VIEW (+Y in):
+----------------------------------------------+
|       shoe body — raised, floats above       |  z = SURROUND_HEIGHT + SHOE_T
|  o   o   [ stadium slot ]   bit hole         |
+----------------------------------------------+  z = SURROUND_HEIGHT (= 4)
                  |                |#######|     <- only the surround boss
              (B) v                |#######|        drops to the work
                                   |__###__|     z = 0 (work surface)
              bearing top ≈ z = 2.5; rolls on the
              work edge for the part below z = 0
```

1. **Surround** (+X end). A small Ø boss (Ø `SURROUND_BOSS_D` = 16,
   height `SURROUND_HEIGHT` = 4) that drops below the raised shoe body to
   touch the work. The bit hole goes through both the boss and the body.
   This boss is the **only** intentional contact patch; the rest of the
   shoe floats above the work.
2. **Bearing channel** (middle). Stadium-shaped slot cut **through the
   full thickness** of the shoe body. The upper sleeve's stem drops into
   this slot from above. Sliding it along X before tightening sets the
   bit-to-bearing distance.
3. **Standoff bolt holes** (−X end). Two M5 clearance through-holes on the
   centerline, spaced `STANDOFF_SPAN` apart.

## Bearing housing assembly

The bearing housing is a two-part sleeve, clamped by an M4 bolt that comes
**up from below** and threads into an embedded **M4 hex nut** captive in
a hex pocket inside the upper sleeve's top flange. (Earlier revisions used
a heat-set insert; the nut is cheaper, stronger threads, and lets the top
flange be much shorter.)

### Stack (bottom → top)

```
M4 bolt head
  → lower_sleeve bottom flange  (under bearing inner race)
  → 608 bearing inner race
  → lower stem | upper Stem 2   (meet end-to-end inside the bore)
  → upper_sleeve thrust step    (rests on bearing inner race top)
  → shoe body bottom face       (clamped by step from below at slot edges)
  → upper_sleeve Stem 1         (in the slot)
  → shoe body top face          (clamped by top flange from above)
  → upper_sleeve top flange     (hex pocket holds captive M4 nut)
```

Note: because the shoe body is raised by `SURROUND_HEIGHT` = 4 mm, the
whole bearing-housing stack is shifted up by the same amount versus the
prior revision. The bearing top now sits at z = 2.5 (was z = −1.5); the
bearing rolls on the work edge over the **lower 4.5 mm** of its OD (the
part below z = 0).

### Clamping

- **Bearing**: inner race compressed between upper step (above) and lower
  flange (below). Outer race is untouched and rotates freely.
- **Shoe**: clamped between the upper sleeve's **top flange (above)** and
  its **thrust step (below)**. Both contact surfaces are on the upper
  sleeve only — the lower sleeve and bearing form a separate compression
  stack hanging below the shoe, so axial slop in the bearing does not
  affect shoe clamping force.

### Thrust-step / lower-flange diameter rule

Both the upper step (Ø `UPPER_STEP_D`) and the lower flange
(Ø `LOWER_FLANGE_D`) are sized to overlap the **608 inner race only**:
larger than the inner race OD (~Ø12) and smaller than the outer race ID
(~Ø16). The rotating outer race never makes friction contact.

## Dimensions (mm)

Constants are mirrored in `cutter.py`. Update both together (see CLAUDE.md).

### Shared

| Constant            | Value | Notes                                   |
|---------------------|------:|-----------------------------------------|
| `BEARING_OD`        | 22.0  | 608 outer diameter                      |
| `BEARING_THK`       | 7.0   | 608 thickness                           |
| `BOLT_CLEARANCE_D`  | 5.5   | M5 clearance                            |
| `M4_BOLT_CLEARANCE_D` | 4.5 | M4 clearance                            |
| `M4_NUT_AF`         | 7.0   | M4 hex nut, across-flats (nominal)      |
| `M4_NUT_T`          | 3.2   | M4 hex nut thickness                    |
| `M4_NUT_POCKET_AF`  | 7.2   | Hex pocket AF (0.1 mm clearance/flat)   |
| `M4_NUT_POCKET_T`   | 3.5   | Hex pocket depth (0.3 mm Z clearance)   |

### Plate (unchanged from v0.1)

| Constant         | Value | Notes                                                                 |
|------------------|------:|-----------------------------------------------------------------------|
| `PLATE_L`        | 90    | X (stadium tip-to-tip)                                                |
| `PLATE_W`        | 30    | Y                                                                     |
| `PLATE_T`        | 10    | Z                                                                     |
| `THREAD_MAJOR`   | 19.05 | Dremel 3/4"-12 UN major Ø                                             |
| `THREAD_PITCH`   | 25.4/12 | ≈ 2.117 mm                                                          |
| `THREAD_X`       | 30    | Bore center on the +X-end semicircle                                  |
| `CHANNEL_W`      | 5.5   | Longitudinal slot Y width (legacy mounting; unused by shoe v0.2)      |
| `CHANNEL_LEN`    | 40    | Slot X length                                                         |
| `CHANNEL_X_CENTER` | -15 | Slot center                                                           |

### Shoe

| Constant         | Value | Notes                                                                |
|------------------|------:|----------------------------------------------------------------------|
| `SHOE_W`         | 30    | Y. Matches PLATE_W.                                                  |
| `SHOE_T`         | 8     | Z thickness of the shoe body. = upper sleeve Stem 1 length.          |
| `SURROUND_HEIGHT`| 4     | Z height of the surround boss (= height the shoe body floats above the work). |
| `SURROUND_WALL`  | 4     | Radial material around the bit hole in the boss.                     |
| `SURROUND_BOSS_D`| 16    | Derived: BIT_HOLE_D + 2·SURROUND_WALL.                               |
| `SURROUND_LEN`   | 14    | X extent reserved for the surround region inside the shoe BODY.      |
| `BIT_HOLE_D`     | 8     | Bit clearance hole through the boss + body.                          |
| `SLOT_LEN`       | 30    | Stadium slot X overall length. Adjustment range = SLOT_LEN − UPPER_STEM1_D = 24 mm. |
| `SLOT_W`         | 6.5   | Slot Y width (= stadium semicircle Ø). Clears UPPER_STEM1_D (Ø6) with ~0.25 mm/side. |
| `END_WALL_FRONT` | 3     | Surround edge → slot edge.                                           |
| `SLOT_END_WALL`  | 3     | Slot edge → standoff bolt edge.                                      |
| `END_WALL_BACK`  | 6     | Outer standoff bolt center → back end of shoe.                       |
| `STANDOFF_BOLT_D`| 5.5   | M5 clearance (= BOLT_CLEARANCE_D).                                   |
| `STANDOFF_SPAN`  | 20    | Bolt-center to bolt-center.                                          |
| `SHOE_L`         | derived (78.75) | Computed from the wall/slot/bolt budget; see source.        |

**Bearing reach (design constraint)**: with these values, when the upper
sleeve is at the front limit of the slot, the bearing's outer edge sits
**2.0 mm from the bit centerline** (and 6.0 mm of shoe wall remains between
the bit hole and the slot front edge). The bit-to-bearing distance ranges
from **13 mm to 37 mm**.

### Upper sleeve

| Constant              | Value | Notes                                                                                |
|-----------------------|------:|--------------------------------------------------------------------------------------|
| `UPPER_STEM2_D`       | 7.8   | Stem inside bearing bore (Ø8) from above.                                            |
| `UPPER_STEM2_L`       | BEARING_THK / 2 = 3.5 | Half the bore depth; meets lower stem mid-bore.                      |
| `UPPER_STEP_D`        | 14    | Thrust step on bearing inner race; clears outer race ID.                             |
| `UPPER_STEP_T`        | 1.5   | Step thickness.                                                                      |
| `UPPER_STEM1_D`       | 6     | Stem in the shoe slot. Just M4 clearance + ~0.75 mm wall.                            |
| `UPPER_STEM1_L`       | SHOE_T = 8 | (consumed at build time)                                                       |
| `UPPER_TOP_FLANGE_D`  | 15    | Sits on shoe body top.                                                               |
| `UPPER_TOP_FLANGE_T`  | 5     | 0.5 mm connecting layer + 3.5 mm hex pocket + 1 mm cap above the nut.                |
| `NUT_POCKET_BOTTOM_LIFT` | 0.5 | Z offset between flange bottom and hex pocket bottom (see below).                |

The M4 hex nut press-fits **upward** into a hex pocket inside the top flange
(open face down toward the bolt). The pocket is offset upward from the
flange bottom by `NUT_POCKET_BOTTOM_LIFT` so a thin 0.5 mm annular layer of
solid material remains under it — without this, the hex (eff. Ø ~7.2)
would slice away the annulus between Stem 1 (Ø6) and the outer flange ring
(Ø15) and split the upper sleeve into two disconnected pieces. The full
M4 bolt path from the bottom of the upper sleeve to the top is just M4
clearance (Ø4.5); the nut is retained axially by the cap above and by the
connecting layer below.

### Lower sleeve

| Constant         | Value | Notes                                                            |
|------------------|------:|------------------------------------------------------------------|
| `LOWER_FLANGE_D` | 14    | Below bearing inner race (same Ø-rule as UPPER_STEP_D).          |
| `LOWER_FLANGE_T` | 1.5   |                                                                  |
| `LOWER_STEM_D`   | 7.8   | Stem inside bearing bore from below.                             |
| `LOWER_STEM_L`   | BEARING_THK − UPPER_STEM2_L = 3.5 | Meets upper Stem 2 end-to-end inside the bore. |

## Build & verify

```sh
uv run python cutter.py
```

Produces in `out/`: `plate.{step,stl}`, `shoe.{step,stl}`,
`upper_sleeve.{step,stl}`, `lower_sleeve.{step,stl}`. If the OCP CAD viewer
extension is running in VS Code, the script also pushes an assembly preview
showing the plate floating above the shoe (at a placeholder standoff height)
and the upper/lower sleeves clamping the bearing in the slot.

Visual checks in the viewer:

- Surround boss sits flat at z = 0; the rest of the shoe body floats at
  z = SURROUND_HEIGHT = 4.
- Stadium-shaped slot passes through the full thickness of the shoe body.
- Upper sleeve top flange on shoe body top, stem fills the slot, step at
  z = SURROUND_HEIGHT covers only the bearing inner race (outer race
  clearance both sides).
- Bearing top ≈ z = SURROUND_HEIGHT − UPPER_STEP_T = 2.5 mm; outer race
  rotates freely; lower 4.5 mm of the bearing OD is below z = 0 to roll
  on the work edge.
- Lower stem and upper Stem 2 meet at the bearing midplane.
- M4 bolt clearance line is unobstructed bottom-to-top; hex nut pocket
  visible inside the top flange.

## Out of scope (next iterations)

- **Standoffs** between shoe and plate.
- **Plate v2**: the existing longitudinal slot is no longer needed once the
  standoffs use fixed bolts to the shoe.
- M4 bolt head choice (socket cap vs. knurled thumbscrew for in-use
  adjustment).
- Alignment features (dowel pins, etc.) between shoe / standoffs / plate.
