"""Purfling cutter — v0.3: plate + shoe + two-part bearing sleeve + washer.

Four printed parts (standoffs are TBD, out of scope here):
- **plate**: 3/4"-12 UN threaded mount for the Dremel nose, unchanged from v0.1.
- **shoe**: pill-shaped body, z=0–SHOE_T, sitting flat on the workpiece.
  The front (surround) region is cut down to a half-stadium snout of width
  SURROUND_BOSS_D and height SURROUND_HEIGHT — the only intentional contact
  patch. A stadium-shaped through-slot in the middle carries the upper sleeve;
  two M5 holes at the back take standoffs.
- **upper_sleeve / lower_sleeve**: two-part bearing housing for a 608 bearing.
  Upper sleeve (Stem 1 + top flange with captive M4 hex nut) installs from
  above through the slot. Lower sleeve (bottom flange + bore stem) installs
  from below; the bearing slides down onto its stem, then the washer sits on
  top of the bearing inner race. M4 bolt from below threads into the nut.
- **washer**: flat ring (Ø WASHER_OD × WASHER_T, M4 clearance bore). Sits on
  top of the bearing inner race, below the shoe, providing the thrust surface
  that contacts the shoe bottom from below. Kept separate so the bearing can
  be assembled onto the lower sleeve without obstruction.

Assembly sequence (bottom → top):
  1. Bearing slides down onto lower sleeve bore stem from above.
  2. Washer placed on bearing inner race top.
  3. Sub-assembly (lower + bearing + washer) brought up to the shoe slot.
  4. Upper sleeve dropped through the slot from above.
  5. M4 bolt inserted from below, threaded into the captive hex nut.

Coordinates
-----------
Shoe-local frame is the world frame for the assembly.
  +X : long axis of the shoe (surround at +X end, standoffs at -X end).
  +Y : short axis (width).
  +Z : up. z = 0 is the bottom of the shoe (sits on workpiece top).
       Shoe body spans z = 0 to z = SHOE_T.
"""

from __future__ import annotations

import math
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildSketch,
    Cylinder,
    GeomType,
    Pos,
    RegularPolygon,
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

# Surround snout: the front of the shoe body is cut to a half-stadium shape
# (flat back, semicircular front) of width SURROUND_BOSS_D and height
# SURROUND_HEIGHT — the only intentional contact patch with the work.
# SURROUND_BOSS_D = BIT_HOLE_D + 2·SURROUND_WALL.
SURROUND_HEIGHT = 4              # Z height of the snout (z=0 to z=4)
SURROUND_WALL = 4                # radial material around the bit hole
BIT_HOLE_D = 8                   # router bit clearance
SURROUND_BOSS_D = BIT_HOLE_D + 2 * SURROUND_WALL  # = 16

# X extent reserved for the surround region cut from the shoe body.
# The snout's flat back is at the -X edge of this region; the semicircle
# center (and bit hole) is at the midpoint (SURROUND_X). Rectangle length
# = SURROUND_LEN/2; semicircle radius = SURROUND_BOSS_D/2.
SURROUND_LEN = 14                # X extent of the surround region

# Bearing channel (through-thickness slot, X-aligned)
SLOT_LEN = 30                    # X adjustment range
SLOT_W = 6.5                     # Y; clears UPPER_STEM1_D=6 + ~0.25/side

# Walls
END_WALL_FRONT = 3               # surround edge → slot edge
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

# ---- bearing housing (two-part sleeve + washer, M4 clamp from below) ---- #
M4_BOLT_CLEARANCE_D = 4.5

# M4 hex nut drops into the upper sleeve top flange from above.
# Standard M4 nut: 7 mm AF, 3.2 mm thick.
M4_NUT_AF = 7.0
M4_NUT_T = 3.2
M4_NUT_POCKET_AF = 7.2           # 0.1 mm clearance per flat
M4_NUT_POCKET_T = 3.5            # pocket depth (nut T + 0.3 mm clearance)

# Upper sleeve: Stem 1 (in slot) + top flange (captive hex nut).
# Installs from above through the slot.
UPPER_STEM1_D = 6                # in the shoe slot
# UPPER_STEM1_L = SHOE_T (consumed at build time)
UPPER_TOP_FLANGE_D = 15          # sits on shoe body top
UPPER_TOP_FLANGE_T = 5           # 1.5 mm solid base + 3.5 mm nut pocket

# Lower sleeve: bottom flange + bore stem (full bearing height, no step).
# Step is replaced by the separate washer so the bearing can slide on freely.
LOWER_FLANGE_D = 14              # below bearing inner race
LOWER_FLANGE_T = 1.5
LOWER_STEM_D = 7.8               # through 608 bore (Ø8), full height
LOWER_STEM_L = BEARING_THK       # = 7.0; fills bore end-to-end

# Washer: sits on top of bearing inner race, below shoe bottom.
# Provides the thrust surface contacting shoe bottom from below.
# Kept separate from the lower sleeve so assembly is possible.
WASHER_OD = 14                   # contacts bearing inner race only (OD < outer race ID ~16)
WASHER_T = 1.5
# Washer bore reuses M4_BOLT_CLEARANCE_D.

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
    # Shoe body: full stadium footprint, z=0 to z=SHOE_T.
    with BuildSketch() as sk:
        SlotOverall(SHOE_L, SHOE_W)
    shoe = extrude(sk.sketch, amount=SHOE_T)

    # Surround region: cut the entire front section (+X end) of the shoe body
    # away, then add back a half-stadium snout (flat back, semicircular front).
    surround_x_start = SURROUND_X - SURROUND_LEN / 2
    shoe -= Pos(surround_x_start - 0.1, 0, -0.1) * Box(
        SURROUND_LEN + SHOE_W / 2 + 0.2,   # extends past the stadium tip
        SHOE_W + 2,
        SHOE_T + 0.2,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )

    # Half-stadium snout: rectangle from the flat back face to the semicircle
    # center, plus a full cylinder at the semicircle center.  The union gives
    # a D-shape — flat back at surround_x_start, rounded front at SURROUND_X.
    # Connection to the shoe body is the full SURROUND_BOSS_D width (vs. the
    # narrow tangent line of a circular snout), giving a stronger joint.
    snout_rect_l = SURROUND_LEN / 2   # = 7 mm rectangle portion
    shoe += Pos(surround_x_start + snout_rect_l / 2, 0, 0) * Box(
        snout_rect_l, SURROUND_BOSS_D, SURROUND_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    shoe += Pos(SURROUND_X, 0, 0) * Cylinder(
        radius=SURROUND_BOSS_D / 2, height=SURROUND_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Bit hole through the snout.
    shoe -= Pos(SURROUND_X, 0, -0.1) * Cylinder(
        radius=BIT_HOLE_D / 2,
        height=SURROUND_HEIGHT + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Bearing channel: stadium-shaped slot through the full body thickness.
    with BuildSketch() as slot_sk:
        SlotOverall(SLOT_LEN, SLOT_W)
    slot_cut = extrude(slot_sk.sketch, amount=SHOE_T + 0.2)
    shoe -= Pos(SLOT_X_CENTER, 0, -0.1) * slot_cut

    # Two standoff bolt holes (M5 clearance through the body).
    for x in (STANDOFF_X_INNER, STANDOFF_X_OUTER):
        shoe -= Pos(x, 0, -0.1) * Cylinder(
            radius=STANDOFF_BOLT_D / 2,
            height=SHOE_T + 0.2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    return shoe


def build_upper_sleeve():
    # Stack (local z=0 = bottom of Stem 1, sits at shoe bottom = world z=0):
    # Stem 1 (in slot) → Top flange (hex nut pocket opens upward).
    body = Cylinder(
        radius=UPPER_STEM1_D / 2, height=SHOE_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body += Pos(0, 0, SHOE_T) * Cylinder(
        radius=UPPER_TOP_FLANGE_D / 2, height=UPPER_TOP_FLANGE_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    flange_top = SHOE_T + UPPER_TOP_FLANGE_T

    # M4 clearance bore through the full sleeve (bolt enters from below).
    body -= Pos(0, 0, -0.1) * Cylinder(
        radius=M4_BOLT_CLEARANCE_D / 2, height=flange_top + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Hex nut pocket opens upward from the flange top; nut drops in from above.
    # The M4 clearance bore (Ø4.5) below the pocket retains the nut axially.
    with BuildSketch() as nut_sk:
        RegularPolygon(
            radius=M4_NUT_POCKET_AF / math.sqrt(3), side_count=6,
        )
    nut_pocket = extrude(nut_sk.sketch, amount=M4_NUT_POCKET_T).solids()[0]
    body -= Pos(0, 0, flange_top - M4_NUT_POCKET_T) * nut_pocket

    return body


def build_lower_sleeve():
    # Stack (local z=0 = bottom of bottom flange):
    # Bottom flange → bore stem (full bearing height).
    # No upper step — that thrust function is handled by the separate washer,
    # which allows the bearing to slide freely onto the stem during assembly.
    body = Cylinder(
        radius=LOWER_FLANGE_D / 2, height=LOWER_FLANGE_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body += Pos(0, 0, LOWER_FLANGE_T) * Cylinder(
        radius=LOWER_STEM_D / 2, height=LOWER_STEM_L,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    total_h = LOWER_FLANGE_T + LOWER_STEM_L
    body -= Pos(0, 0, -0.1) * Cylinder(
        radius=M4_BOLT_CLEARANCE_D / 2, height=total_h + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return body


def build_washer():
    # Flat ring: sits on bearing inner race top, below shoe bottom.
    # Provides the thrust surface that clamps the shoe from below.
    body = Cylinder(
        radius=WASHER_OD / 2, height=WASHER_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body -= Pos(0, 0, -0.1) * Cylinder(
        radius=M4_BOLT_CLEARANCE_D / 2, height=WASHER_T + 0.2,
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
    washer = build_washer()

    export_step(plate, str(OUT / "plate.step"))
    export_stl(plate, str(OUT / "plate.stl"))
    export_step(shoe, str(OUT / "shoe.step"))
    export_stl(shoe, str(OUT / "shoe.stl"))
    export_step(upper_sleeve, str(OUT / "upper_sleeve.step"))
    export_stl(upper_sleeve, str(OUT / "upper_sleeve.stl"))
    export_step(lower_sleeve, str(OUT / "lower_sleeve.step"))
    export_stl(lower_sleeve, str(OUT / "lower_sleeve.stl"))
    export_step(washer, str(OUT / "washer.step"))
    export_stl(washer, str(OUT / "washer.stl"))
    print(f"Exported: {sorted(p.name for p in OUT.iterdir())}")

    # ---- assembly preview (world frame = shoe-local) ---- #
    # Bearing center at the slot midpoint for the preview.
    bearing_x = SLOT_X_CENTER

    # Upper sleeve: local z=0 at shoe bottom (world z=0); flange above shoe top.
    upper_assembled = Pos(bearing_x, 0, 0) * upper_sleeve

    # Washer top = shoe bottom = world z=0; washer sits on bearing inner race top.
    washer_z_base = -WASHER_T
    washer_assembled = Pos(bearing_x, 0, washer_z_base) * washer

    # Bearing: inner race top at z = -WASHER_T; outer race rolls on work edge.
    bearing_top_z = -WASHER_T
    bearing_bottom_z = bearing_top_z - BEARING_THK
    bearing_ghost = Cylinder(
        radius=BEARING_OD / 2, height=BEARING_THK,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ) - Cylinder(
        radius=LOWER_STEM_D / 2 + 0.05, height=BEARING_THK + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    bearing_ghost = Pos(bearing_x, 0, bearing_bottom_z) * bearing_ghost

    # Lower sleeve: bore stem top at bearing_top_z; flange below bearing.
    lower_z_base = bearing_bottom_z - LOWER_FLANGE_T
    lower_assembled = Pos(bearing_x, 0, lower_z_base) * lower_sleeve

    # Plate: floats above the shoe at STANDOFF_VIS_H, threaded bore over bit hole.
    plate_assembled = Pos(
        SURROUND_X - THREAD_X, 0, SHOE_T + STANDOFF_VIS_H
    ) * plate

    try:
        from ocp_vscode import show
        show(
            plate_assembled, shoe, upper_assembled, lower_assembled,
            washer_assembled, bearing_ghost,
            names=["plate", "shoe", "upper_sleeve", "lower_sleeve",
                   "washer", "bearing"],
        )
        print("Sent to OCP CAD Viewer.")
    except ImportError:
        print("ocp_vscode not installed; skipping viewer.")
    except Exception as exc:
        print(f"Viewer unavailable (is the VS Code extension running?): {exc}")


if __name__ == "__main__":
    main()
