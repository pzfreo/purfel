"""Purfling cutter — v0.2: plate + shoe + two-part bearing sleeve.

Three printed parts (standoffs are TBD, out of scope here):
- **plate**: 3/4"-12 UN threaded mount for the Dremel nose, unchanged from v0.1.
- **shoe**: low pill-shaped sole that sits on the work at z=0. Has a bit hole
  (front), a through-thickness slot for the bearing sleeve (middle), and two
  M5 standoff bolt holes (back), all on the shoe's centerline.
- **upper_sleeve / lower_sleeve**: two-part bearing housing, captive on a 608
  bearing. Clamped by an M4 bolt from below that threads into an M4 heat-set
  insert in the upper sleeve. Sliding the upper sleeve along the shoe slot
  before tightening sets the bit-to-bearing distance.

Coordinates
-----------
Shoe-local frame is the world frame for the assembly.
  +X : long axis of the shoe (surround at +X end, standoffs at -X end).
  +Y : short axis (width).
  +Z : up. z = 0 is the shoe bottom (sits on workpiece top).
"""

from __future__ import annotations

from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildSketch,
    Cylinder,
    GeomType,
    Pos,
    SlotOverall,
    chamfer,
    export_step,
    export_stl,
    extrude,
)
from bd_warehouse.thread import IsoThread

# ---- plate (unchanged from v0.1) ---- #
PLATE_L = 90
PLATE_W = 30
PLATE_T = 10

# Dremel 3/4"-12 UN
THREAD_MAJOR = 19.05
THREAD_PITCH = 25.4 / 12

THREAD_X = PLATE_L / 2 - PLATE_W / 2

CHANNEL_W = 5.5
CHANNEL_LEN = 40
CHANNEL_X_CENTER = -15

# ---- 608 bearing (shared) ---- #
BEARING_OD = 22.0
BEARING_THK = 7.0
# Inner race OD ≈ 12, outer race ID ≈ 16. Step/flange Ø sits between.

# ---- M5 (standoff bolts, shared with v0.1 plate inserts) ---- #
BOLT_CLEARANCE_D = 5.5
INSERT_HOLE_D = 6.7
INSERT_HOLE_DEPTH = 8.5
INSERT_CHAMFER = 0.5

# ---- shoe ---- #
SHOE_W = 30                      # Y, matches PLATE_W
SHOE_T = 8                       # Z; = upper sleeve Stem 1 length

# Surround region (front, contains bit hole)
SURROUND_LEN = 22                # X extent reserved for surround
BIT_HOLE_D = 8                   # router bit clearance (TODO: pick real bit)

# Bearing channel (through-thickness slot, X-aligned)
SLOT_LEN = 30                    # X adjustment range
SLOT_W = 8.5                     # Y; clears UPPER_STEM1_D=8 + ~0.25/side

# Walls
END_WALL_FRONT = 6               # surround edge → slot edge
SLOT_END_WALL = 3                # slot edge → standoff bolt edge
END_WALL_BACK = 6                # outer standoff bolt center → back end

# Standoff bolt holes (M5 clearance, two on centerline)
STANDOFF_BOLT_D = BOLT_CLEARANCE_D
STANDOFF_SPAN = 20               # bolt-center to bolt-center

# Derived shoe length and feature X positions (shoe centered at X=0).
SHOE_L = (
    SURROUND_LEN
    + END_WALL_FRONT
    + SLOT_LEN
    + SLOT_END_WALL
    + STANDOFF_BOLT_D / 2
    + STANDOFF_SPAN
    + END_WALL_BACK
)
SURROUND_X = SHOE_L / 2 - SURROUND_LEN / 2
SLOT_X_CENTER = (
    SURROUND_X - SURROUND_LEN / 2 - END_WALL_FRONT - SLOT_LEN / 2
)
STANDOFF_X_INNER = (
    SLOT_X_CENTER - SLOT_LEN / 2 - SLOT_END_WALL - STANDOFF_BOLT_D / 2
)
STANDOFF_X_OUTER = STANDOFF_X_INNER - STANDOFF_SPAN

# ---- bearing housing (two-part sleeve, M4 clamp from below) ---- #
M4_BOLT_CLEARANCE_D = 4.5
M4_INSERT_HOLE_D = 5.7           # OD of brass M4 insert pocket
M4_INSERT_LEN = 8                # depth of insert pocket

# Upper sleeve stack (built bottom→top, Stem 2 base at local z=0).
UPPER_STEM2_D = 7.8              # into 608 bore from above
UPPER_STEM2_L = BEARING_THK / 2  # = 3.5; meets lower stem mid-bore
UPPER_STEP_D = 14                # thrust step on bearing inner race
UPPER_STEP_T = 1.5
UPPER_STEM1_D = 8                # in the shoe slot
# UPPER_STEM1_L = SHOE_T (consumed at build time)
UPPER_TOP_FLANGE_D = 15          # sits on shoe top
UPPER_TOP_FLANGE_T = 3

# Lower sleeve stack (built bottom→top, bottom flange at local z=0).
LOWER_FLANGE_D = 14              # below bearing inner race
LOWER_FLANGE_T = 1.5
LOWER_STEM_D = 7.8               # into 608 bore from below
LOWER_STEM_L = BEARING_THK - UPPER_STEM2_L  # = 3.5

OUT = Path(__file__).parent / "out"


def build_plate():
    with BuildSketch() as sk:
        SlotOverall(PLATE_L, PLATE_W)
    plate = extrude(sk.sketch, amount=PLATE_T)

    plate -= Pos(THREAD_X, 0, -0.1) * Cylinder(
        radius=THREAD_MAJOR / 2,
        height=PLATE_T + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    thread = IsoThread(
        major_diameter=THREAD_MAJOR,
        pitch=THREAD_PITCH,
        length=PLATE_T,
        external=False,
        end_finishes=("chamfer", "chamfer"),
    )
    plate += Pos(THREAD_X, 0, 0) * thread

    plate -= Pos(CHANNEL_X_CENTER, 0, -0.1) * Box(
        CHANNEL_LEN, CHANNEL_W, PLATE_T + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return plate


def build_shoe():
    # Stadium footprint, extruded to SHOE_T. Bottom at z=0, top at z=SHOE_T.
    with BuildSketch() as sk:
        SlotOverall(SHOE_L, SHOE_W)
    shoe = extrude(sk.sketch, amount=SHOE_T)

    # Bit hole through the surround.
    shoe -= Pos(SURROUND_X, 0, -0.1) * Cylinder(
        radius=BIT_HOLE_D / 2,
        height=SHOE_T + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Bearing channel: through-thickness rectangular slot.
    shoe -= Pos(SLOT_X_CENTER, 0, -0.1) * Box(
        SLOT_LEN, SLOT_W, SHOE_T + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Two standoff bolt holes (M5 clearance through the full thickness).
    for x in (STANDOFF_X_INNER, STANDOFF_X_OUTER):
        shoe -= Pos(x, 0, -0.1) * Cylinder(
            radius=STANDOFF_BOLT_D / 2,
            height=SHOE_T + 0.2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    return shoe


def build_upper_sleeve():
    # Stack: Stem 2 (in-bore) → Step → Stem 1 (in-slot) → Top flange.
    z = 0.0
    body = Pos(0, 0, z) * Cylinder(
        radius=UPPER_STEM2_D / 2, height=UPPER_STEM2_L,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    z += UPPER_STEM2_L
    body += Pos(0, 0, z) * Cylinder(
        radius=UPPER_STEP_D / 2, height=UPPER_STEP_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    z += UPPER_STEP_T
    body += Pos(0, 0, z) * Cylinder(
        radius=UPPER_STEM1_D / 2, height=SHOE_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    z += SHOE_T
    body += Pos(0, 0, z) * Cylinder(
        radius=UPPER_TOP_FLANGE_D / 2, height=UPPER_TOP_FLANGE_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    total_h = z + UPPER_TOP_FLANGE_T

    # M4 insert pocket from the BOTTOM (insert is pressed in from below,
    # open end facing the M4 bolt that comes up from below).
    body -= Pos(0, 0, -0.01) * Cylinder(
        radius=M4_INSERT_HOLE_D / 2, height=M4_INSERT_LEN + 0.01,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # M4 clearance above the insert pocket up through the top flange.
    body -= Pos(0, 0, M4_INSERT_LEN) * Cylinder(
        radius=M4_BOLT_CLEARANCE_D / 2,
        height=total_h - M4_INSERT_LEN + 0.1,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return body


def build_lower_sleeve():
    # Stack: bottom flange → stem (into bore from below).
    body = Cylinder(
        radius=LOWER_FLANGE_D / 2, height=LOWER_FLANGE_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body += Pos(0, 0, LOWER_FLANGE_T) * Cylinder(
        radius=LOWER_STEM_D / 2, height=LOWER_STEM_L,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # M4 clearance through the whole part.
    body -= Pos(0, 0, -0.1) * Cylinder(
        radius=M4_BOLT_CLEARANCE_D / 2,
        height=LOWER_FLANGE_T + LOWER_STEM_L + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body


# Visualization-only standoff height (so the plate floats above the shoe in
# the viewer at a plausible offset). The standoffs themselves aren't designed.
STANDOFF_VIS_H = 50


def main() -> None:
    OUT.mkdir(exist_ok=True)
    plate = build_plate()
    shoe = build_shoe()
    upper_sleeve = build_upper_sleeve()
    lower_sleeve = build_lower_sleeve()

    export_step(plate, str(OUT / "plate.step"))
    export_stl(plate, str(OUT / "plate.stl"))
    export_step(shoe, str(OUT / "shoe.step"))
    export_stl(shoe, str(OUT / "shoe.stl"))
    export_step(upper_sleeve, str(OUT / "upper_sleeve.step"))
    export_stl(upper_sleeve, str(OUT / "upper_sleeve.stl"))
    export_step(lower_sleeve, str(OUT / "lower_sleeve.step"))
    export_stl(lower_sleeve, str(OUT / "lower_sleeve.stl"))
    print(f"Exported: {sorted(p.name for p in OUT.iterdir())}")

    # ---- assembly preview (world frame = shoe-local) ---- #
    # Bearing center at the slot midpoint for the preview.
    bearing_x = SLOT_X_CENTER

    # Upper sleeve: Stem 2 base at world z = -(UPPER_STEM2_L + UPPER_STEP_T)
    # so the step's TOP face sits flush at z=0 (= shoe bottom in slot region).
    upper_z_base = -(UPPER_STEM2_L + UPPER_STEP_T)
    upper_assembled = Pos(bearing_x, 0, upper_z_base) * upper_sleeve

    # Bearing: top at world z = -UPPER_STEP_T (just below upper step).
    bearing_top_z = -UPPER_STEP_T
    bearing_bottom_z = bearing_top_z - BEARING_THK
    bearing_ghost = Cylinder(
        radius=BEARING_OD / 2, height=BEARING_THK,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ) - Cylinder(
        radius=UPPER_STEM2_D / 2 + 0.05, height=BEARING_THK + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    bearing_ghost = Pos(bearing_x, 0, bearing_bottom_z) * bearing_ghost

    # Lower sleeve: flange BOTTOM at world z = bearing_bottom_z - LOWER_FLANGE_T
    # so the flange's TOP face contacts the bearing inner race bottom.
    lower_z_base = bearing_bottom_z - LOWER_FLANGE_T
    lower_assembled = Pos(bearing_x, 0, lower_z_base) * lower_sleeve

    # Plate: floats above the shoe at STANDOFF_VIS_H, aligned so the threaded
    # bore sits over the shoe's bit hole (visualization only — standoffs TBD).
    plate_assembled = Pos(
        SURROUND_X - THREAD_X, 0, SHOE_T + STANDOFF_VIS_H
    ) * plate

    try:
        from ocp_vscode import show
        show(
            plate_assembled, shoe, upper_assembled, lower_assembled,
            bearing_ghost,
            names=["plate", "shoe", "upper_sleeve", "lower_sleeve", "bearing"],
        )
        print("Sent to OCP CAD Viewer.")
    except ImportError:
        print("ocp_vscode not installed; skipping viewer.")
    except Exception as exc:
        print(f"Viewer unavailable (is the VS Code extension running?): {exc}")


if __name__ == "__main__":
    main()
