# Purfling Cutter — Design Spec (v0.4)

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
| `shoe`          | Stadium-shaped body sitting flat on the work (z=0–SHOE_T). Front (surround) region is cut to a half-stadium snout (flat back, Ø16 semicircular front, 4 mm tall) — the only contact patch. Houses the bit hole, the stadium-shaped bearing slot, and standoff bolt holes. | `build_shoe()` |
| `upper_sleeve`  | Drops into the shoe slot from above (Stem 1 + top flange); top flange carries the captive M4 hex nut (drops in from above). | `build_upper_sleeve()` |
| `lower_sleeve`  | Installs from below; bottom flange under bearing inner race, bore stem through full bearing height. No upper step — bearing slides freely onto stem during assembly. | `build_lower_sleeve()` |
| `washer`        | Flat ring (Ø14 × 1.5 mm, M4 clearance bore). Sits on bearing inner race top below the shoe; provides the thrust surface that clamps the shoe from below. Placed after bearing is assembled onto lower sleeve. | `build_washer()` |
| 608 bearing     | Edge follower (Ø22 OD × Ø8 bore × 7 mm).                                 | sourced                 |
| M4 bolt         | Clamps the sleeve stack from below into the upper sleeve's captive nut.   | sourced (M4 × ~25)      |
| M4 hex nut      | Drops into the hex pocket in the upper sleeve top flange from above.     | sourced (7 mm AF × 3.2) |

## Coordinate system

Shoe-local frame is the world frame for the assembly.

- **+X**: long axis of the shoe (surround at +X end, standoffs at −X end).
- **+Y**: short axis (width).
- **+Z**: up. **z = 0 is the bottom face of the shoe**, which rests on the
  workpiece. The shoe body spans z = 0 to z = `SHOE_T` (= 8). The surround
  snout occupies the front region from z = 0 to z = `SURROUND_HEIGHT` (= 4);
  the rest of the front is cut away.

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
|       shoe body — full thickness, z=0–SHOE_T |  z = SHOE_T = 8
|  o   o   [ stadium slot ]   | snout only |   |
+-----------------------------+             +   |  z = SURROUND_HEIGHT = 4
                              |             |   |
                              |_____________|   |  z = 0 (work surface)
              (B) v                              <- snout is only contact patch
           bearing top ≈ z = -LOWER_STEP_T = -1.5
           bearing rolls on work edge below z=0
```

1. **Surround** (+X end). The front region of the shoe body (X extent
   `SURROUND_LEN` = 14) is cut to a **half-stadium** snout: flat back face at
   the surround region edge, semicircular front of radius `SURROUND_BOSS_D`/2
   = 8, height `SURROUND_HEIGHT` = 4. The flat back gives a 16 mm-wide joint
   to the shoe body (vs. the ~8 mm tangent contact of a circular snout),
   improving stiffness. The bit hole goes through the snout at `SURROUND_X`.
2. **Bearing channel** (middle). Stadium-shaped slot cut **through the
   full thickness** of the shoe body. The upper sleeve's Stem 1 drops into
   this slot from above. Sliding it along X before tightening sets the
   bit-to-bearing distance.
3. **Standoff bolt holes** (−X end). Two M5 clearance through-holes on the
   centerline, spaced `STANDOFF_SPAN` apart.

## Bearing housing assembly

The bearing housing is a two-part sleeve, clamped by an M4 bolt that comes
**up from below** and threads into an embedded **M4 hex nut** that drops
into a pocket in the upper sleeve's top flange from above.

### Upper sleeve

- **Stem 1** (Ø `UPPER_STEM1_D` = 6, length `SHOE_T` = 8): fits through the
  slot; the narrow diameter means the upper sleeve can install vertically from
  above through the slot.
- **Top flange** (Ø `UPPER_TOP_FLANGE_D` = 15, thickness `UPPER_TOP_FLANGE_T`
  = 5): sits on the shoe body top and clamps the shoe from above. Contains the
  hex nut pocket (opens upward; nut drops in from the top).

### Lower sleeve

- **Bottom flange** (Ø `LOWER_FLANGE_D` = 14): under the bearing inner race.
- **Bore stem** (Ø `LOWER_STEM_D` = 7.8, length `LOWER_STEM_L` =
  `BEARING_THK` = 7.0): fills the bearing bore end-to-end. No upper step —
  the bearing slides freely onto the stem from above during assembly.

### Washer

- Ø `WASHER_OD` = 14, thickness `WASHER_T` = 1.5, M4 clearance bore.
- Placed on the bearing inner race top after the bearing is assembled onto the
  lower sleeve. Provides the thrust surface that contacts the shoe bottom (z = 0)
  from below.

### Assembly sequence

1. Bearing slides down onto lower sleeve bore stem from above (stem Ø7.8, bore Ø8).
2. Washer placed on bearing inner race top.
3. Sub-assembly (lower sleeve + bearing + washer) raised to the shoe slot from below.
4. Upper sleeve dropped through the slot from above (Stem 1 in slot, flange on top).
5. M4 bolt inserted from below; threaded into captive hex nut in upper flange.

### Stack (bottom → top)

```
M4 bolt head
  → lower_sleeve bottom flange  (under bearing inner race)
  → lower_sleeve bore stem      (fills bearing bore)
  → washer                      (on bearing inner race top; contacts shoe bottom)
  → shoe body bottom face       (slot edges clamped between washer and upper flange)
  → upper_sleeve Stem 1         (in the slot)
  → shoe body top face
  → upper_sleeve top flange     (hex pocket holds captive M4 nut)
```

### Clamping

- **Bearing**: inner race compressed between washer (above) and lower sleeve
  bottom flange (below). Outer race is untouched and rotates freely.
- **Shoe**: clamped between the upper sleeve's **top flange (above)** and the
  **washer (below)**. Tightening the M4 bolt pulls the lower sleeve + washer
  stack up against the shoe bottom; the upper sleeve's flange resists from above.

### Washer / flange diameter rule

Both `WASHER_OD` and `LOWER_FLANGE_D` (both = 14) are sized to overlap the
**608 inner race only**: larger than the inner race OD (~Ø12) and smaller than
the outer race ID (~Ø16). The rotating outer race never makes friction contact.

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
| `M4_NUT_POCKET_T`   | 3.5   | Hex pocket depth (nut T + 0.3 mm)       |

### Plate (unchanged from v0.1)

| Constant         | Value | Notes                                                                 |
|------------------|------:|-----------------------------------------------------------------------|
| `PLATE_L`        | 90    | X (stadium tip-to-tip)                                                |
| `PLATE_W`        | 30    | Y                                                                     |
| `PLATE_T`        | 10    | Z                                                                     |
| `THREAD_MAJOR`   | 19.05 | Dremel 3/4"-12 UN major Ø                                             |
| `THREAD_PITCH`   | 25.4/12 | ≈ 2.117 mm                                                          |
| `THREAD_X`       | 30    | Bore center on the +X-end semicircle                                  |
| `CHANNEL_W`      | 5.5   | Longitudinal slot Y width (legacy mounting; unused by shoe v0.3)      |
| `CHANNEL_LEN`    | 40    | Slot X length                                                         |
| `CHANNEL_X_CENTER` | -15 | Slot center                                                           |

### Shoe

| Constant         | Value | Notes                                                                |
|------------------|------:|----------------------------------------------------------------------|
| `SHOE_W`         | 30    | Y. Matches PLATE_W.                                                  |
| `SHOE_T`         | 8     | Z thickness of the shoe body. = upper sleeve Stem 1 length.          |
| `SURROUND_HEIGHT`| 4     | Z height of the surround snout (z=0 to z=4).                         |
| `SURROUND_WALL`  | 4     | Radial material around the bit hole in the snout.                    |
| `SURROUND_BOSS_D`| 16    | Derived: BIT_HOLE_D + 2·SURROUND_WALL.                               |
| `SURROUND_LEN`   | 14    | X extent of the surround region cut from the shoe body.              |
| `BIT_HOLE_D`     | 8     | Bit clearance hole through the snout.                                |
| `SLOT_LEN`       | 30    | Stadium slot X overall length. Adjustment range = SLOT_LEN − UPPER_STEM1_D = 24 mm. |
| `SLOT_W`         | 6.5   | Slot Y width (= stadium semicircle Ø). Clears UPPER_STEM1_D (Ø6) with ~0.25 mm/side. |
| `END_WALL_FRONT` | 3     | Surround edge → slot edge.                                           |
| `SLOT_END_WALL`  | 3     | Slot edge → standoff bolt edge.                                      |
| `END_WALL_BACK`  | 6     | Outer standoff bolt center → back end of shoe.                       |
| `STANDOFF_BOLT_D`| 5.5   | M5 clearance (= BOLT_CLEARANCE_D).                                   |
| `STANDOFF_SPAN`  | 20    | Bolt-center to bolt-center.                                          |
| `SHOE_L`         | derived (78.75) | Computed from the wall/slot/bolt budget; see source.        |

### Upper sleeve

| Constant              | Value | Notes                                                                                |
|-----------------------|------:|--------------------------------------------------------------------------------------|
| `UPPER_STEM1_D`       | 6     | Stem in the shoe slot. Fits through SLOT_W (6.5) with ~0.25 mm/side clearance.      |
| `UPPER_TOP_FLANGE_D`  | 15    | Sits on shoe body top.                                                               |
| `UPPER_TOP_FLANGE_T`  | 5     | 1.5 mm solid base below nut pocket + 3.5 mm hex pocket from top.                    |

The M4 hex nut drops into the hex pocket from above (pocket opens upward).
The M4 clearance bore (Ø4.5) below the pocket is smaller than the nut AF (7 mm),
so the nut cannot fall through. When the bolt is tightened, it threads into the
nut; the hex walls prevent rotation; the nut is pulled down against the pocket floor.

### Lower sleeve

| Constant         | Value | Notes                                                            |
|------------------|------:|------------------------------------------------------------------|
| `LOWER_FLANGE_D` | 14    | Below bearing inner race (inner-race-only rule).                 |
| `LOWER_FLANGE_T` | 1.5   |                                                                  |
| `LOWER_STEM_D`   | 7.8   | Stem through bearing bore (608 bore = Ø8).                       |
| `LOWER_STEM_L`   | 7.0   | = BEARING_THK; fills bore end-to-end.                            |

### Washer

| Constant     | Value | Notes                                                                |
|--------------|------:|----------------------------------------------------------------------|
| `WASHER_OD`  | 14    | Contacts bearing inner race only; clears outer race ID (~Ø16).       |
| `WASHER_T`   | 1.5   | Thrust thickness between bearing inner race top and shoe bottom.     |

## Build & verify

```sh
uv run python cutter.py
```

Produces in `out/`: `plate.{step,stl}`, `shoe.{step,stl}`,
`upper_sleeve.{step,stl}`, `lower_sleeve.{step,stl}`, `washer.{step,stl}`.
If the OCP CAD viewer extension is running in VS Code, the script also pushes
an assembly preview.

Visual checks in the viewer:

- Shoe body spans z = 0 to z = SHOE_T = 8. Surround region is a half-stadium
  snout (flat back, Ø16 rounded front, 4 mm tall); rest of the front is gone.
- Stadium-shaped slot passes through the full thickness of the shoe body.
- Upper sleeve: Stem 1 in the slot, top flange on shoe body top. Hex pocket
  visible (opening upward) inside the top flange.
- Lower sleeve: bore stem top at bearing inner race top; bottom flange below.
  No step on the lower sleeve.
- Washer: flat ring between bearing inner race top and shoe bottom (z = −WASHER_T
  to z = 0).
- Bearing top ≈ z = −WASHER_T = −1.5; outer race rotates freely; outer race
  rolls on the work edge below z = 0.
- M4 bolt clearance line is unobstructed bottom-to-top.

## Out of scope (next iterations)

- **Standoffs** between shoe and plate.
- **Plate v2**: the existing longitudinal slot is no longer needed once the
  standoffs use fixed bolts to the shoe.
- M4 bolt head choice (socket cap vs. knurled thumbscrew for in-use adjustment).
- Alignment features (dowel pins, etc.) between shoe / standoffs / plate.
- M4 bolt head choice (socket cap vs. knurled thumbscrew for in-use adjustment).
