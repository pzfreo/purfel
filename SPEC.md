# Purfling Cutter — Design Spec (v0.2)

A 3D-printed jig that holds a Dremel rotary tool over a stringed-instrument
top so a cutter bit can rout a constant-distance channel from the edge,
following the body's perimeter via a bearing.

This document describes the **as-built** design in `cutter.py`. Constant
names below match constants in the source.

## Parts

Three printed parts plus a sourced bearing and an M4 bolt + heat-set insert.
Standoffs that connect shoe to plate are **not yet designed** and remain out
of scope here.

| Part            | Function                                                                 | Source                  |
|-----------------|--------------------------------------------------------------------------|-------------------------|
| `plate`         | Holds the Dremel via a 3/4"-12 UN internal thread.                       | `build_plate()`         |
| `shoe`          | Sits on the workpiece. Houses the bit hole, bearing slot, and standoff bolt holes. | `build_shoe()`  |
| `upper_sleeve`  | Drops into the shoe slot from above; clamps the shoe; rides on bearing inner race. | `build_upper_sleeve()` |
| `lower_sleeve`  | Goes into the bearing bore from below; captures the bearing inner race.  | `build_lower_sleeve()`  |
| 608 bearing     | Edge follower (Ø22 OD × Ø8 bore × 7 mm).                                 | sourced                 |
| M4 bolt         | Clamps the sleeve stack from below into the upper sleeve's M4 insert.     | sourced (M4 × ~25)      |
| M4 brass insert | Threaded anchor in the upper sleeve.                                     | sourced (Ø5.6 × 8 mm)   |

## Coordinate system

Shoe-local frame is the world frame for the assembly.

- **+X**: long axis of the shoe (surround at +X end, standoffs at −X end).
- **+Y**: short axis (width).
- **+Z**: up. **z = 0 is the shoe bottom**, which sits on the workpiece top.

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
+--------+        +-----+        +---------+
|        |        |     |        |         |  z = SHOE_T
|  back  |        |     |  slot  |  surr   |
|________|________|_____|________|_________|  z = 0 (work surface)
                    (B)                        bearing dangles below z=0
                     |                         top of bearing ≈ z = 0
                     v                         outer race rolls on work edge
                  z < 0
```

1. **Surround** (+X end). Solid, full-thickness section with a through-hole
   sized for the router bit + clearance. Bottom face at z = 0; this is the
   intentional contact patch with the work and sets the jig height.
2. **Bearing channel** (middle). Rectangular slot cut **through the full
   thickness** of the shoe. The upper sleeve's stem drops into this slot
   from above. Sliding it along X before tightening sets the bit-to-bearing
   distance.
3. **Standoff bolt holes** (−X end). Two M5 clearance through-holes on the
   centerline, spaced `STANDOFF_SPAN` apart.

## Bearing housing assembly

The bearing housing is a two-part sleeve, clamped by an M4 bolt that comes
**up from below** and threads into an M4 heat-set insert in the upper
sleeve.

### Stack (bottom → top)

```
M4 bolt head
  → lower_sleeve bottom flange  (under bearing inner race)
  → 608 bearing inner race
  → lower stem | upper Stem 2   (meet end-to-end inside the bore)
  → upper_sleeve thrust step    (rests on bearing inner race top)
  → shoe bottom face            (clamped by step from below at slot edges)
  → upper_sleeve Stem 1         (in the slot)
  → shoe top face               (clamped by top flange from above)
  → upper_sleeve top flange     (contains the M4 insert in its upper 8 mm)
```

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
| `M4_INSERT_HOLE_D`  | 5.7   | OD of M4 brass heat-set insert pocket   |
| `M4_INSERT_LEN`     | 8     | Insert pocket depth                     |

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
| `SHOE_T`         | 8     | Z. = upper sleeve Stem 1 length.                                     |
| `SURROUND_LEN`   | 14    | X extent reserved for the surround (front of shoe).                  |
| `BIT_HOLE_D`     | 8     | Bit clearance hole through the surround.                             |
| `SLOT_LEN`       | 30    | Bearing slot X length. Adjustment range = SLOT_LEN − UPPER_STEM1_D = 24 mm. |
| `SLOT_W`         | 6.5   | Slot Y width. Clears UPPER_STEM1_D (Ø6) with ~0.25 mm/side.          |
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
| `UPPER_TOP_FLANGE_D`  | 15    | Sits on shoe top.                                                                    |
| `UPPER_TOP_FLANGE_T`  | 9     | Tall enough to fully contain the M4 insert (8 mm) with a 1 mm cap above.             |

The M4 insert lives **inside the top flange** (not in Stem 1), because Stem 1
at Ø6 has insufficient wall around the Ø5.7 insert. The full path from the
bottom of the upper sleeve up to the top flange is just M4 bolt clearance
(Ø4.5).

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

- Surround sits flat at z = 0.
- Slot passes through the full shoe thickness.
- Upper sleeve top flange on shoe top, stem fills the slot, step at z = 0
  covers only the bearing inner race (outer race clearance both sides).
- Bearing top ≈ z = −UPPER_STEP_T = −1.5 mm; outer race rotates freely.
- Lower stem and upper Stem 2 meet at the bearing midplane.
- M4 bolt clearance line is unobstructed bottom-to-top.

## Out of scope (next iterations)

- **Standoffs** between shoe and plate.
- **Plate v2**: the existing longitudinal slot is no longer needed once the
  standoffs use fixed bolts to the shoe.
- M4 bolt head choice (socket cap vs. knurled thumbscrew for in-use
  adjustment).
- Underside relief on the shoe to make the surround the only contact
  patch (currently the whole bottom is flat at z = 0).
- Alignment features (dowel pins, etc.) between shoe / standoffs / plate.
