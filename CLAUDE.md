# Purfel — Claude project notes

## Keep `SPEC.md` and `cutter.py` in sync

`SPEC.md` is the design spec for the cutter. It describes the as-built
geometry, the constants, the assembly stack, and the clamping rules. The
spec and `cutter.py` are a **coupled pair** — drift between them is a bug.

When you change `cutter.py`:

- If you add, rename, remove, or re-value a constant that appears in
  `SPEC.md`'s tables, update the table in the same change.
- If you change the geometry (stack order, what clamps what, where a
  feature lives, slot/hole/flange topology), update the relevant prose
  section and any ASCII diagrams.
- If you add or remove a `build_*` function or an exported file, update
  the **Parts** table and the **Build & verify** section.
- If a constraint that the spec calls out (e.g. the inner-race-only
  Ø-rule for `UPPER_STEP_D` / `LOWER_FLANGE_D`) changes, update the
  rationale in the spec — don't just change the number.

When you change `SPEC.md` first as part of planning, propagate the same
decisions into `cutter.py` in the same change so they don't diverge.

A small change in one file usually warrants a one- or two-line change in
the other; don't skip it because the source feels self-explanatory — the
spec is the authoritative description of *intent*.
