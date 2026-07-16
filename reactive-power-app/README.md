# Reactive Power Compensation Sizing App

An interactive web app built from the `Reactive_Power_Compensation_Belvior.xlsx`
worksheet. It sizes the reactive power compensation for a utility-scale solar PV
plant and determines how many inverters are needed to meet both the grid
injection limit and the reactive power demand.

**Run it:** open `index.html` in any browser — it is fully self-contained
(no build step, no dependencies, works offline).

## Calculation chain (same as the worksheet)

1. **Initial sizing** — grid injection limit and required power factor give the
   plant MVA rating (`P / cos φ`) and the grid's MVAr demand (`√(S² − P²)`).
2. **Transformer reactive consumption** — per group: `Q = count × rating × Z%`,
   summed with a design margin (10 % in the worksheet).
3. **Internal system losses** — PVsyst loss fractions applied to the grid limit
   (AC cable, auxiliary system, transmission line, miscellaneous).
4. **Inverter capability** — per-inverter reactive capability `√(S² − P²)` at
   the chosen inverter power factor, required inverter count
   `⌈Q_total / q_inv⌉`, and the net power actually delivered to the grid.
5. **Reactive capability vs grid voltage** *(new, not in the worksheet)* — the
   plant's reactive capability evaluated across a grid-voltage band
   (default 0.80–1.15 p.u., editable). Below 1.00 p.u. the inverter is
   current-limited, so apparent power scales with voltage
   (`S(V) = V × S_rated`); above 1.00 p.u. it holds rated apparent power.
   Active power is dispatched first (P-priority) and the remainder is available
   as reactive power: `q(V) = √(S(V)² − p²)`. Each level gets a pass/fail
   verdict against the reactive demand, with active-power-curtailment flagging
   when `S(V) < p`, plus a capability curve chart with hover details.

The engine was verified against the workbook's cached values: all intermediate
and final results (MVA rating, MVAr demand, transformer demand, losses,
apparent power, inverter count 164, delivered power 52.908 MW) match exactly.

## Improvements over the spreadsheet

- **Live recalculation** — every result updates as you type.
- **Built-in Goal Seek** — replaces Excel's manual *Data ▸ What-If Analysis ▸
  Goal Seek* step. It solves analytically for the minimum inverter count that
  meets both the active requirement (grid limit + losses) and the reactive
  requirement, and reports the full feasible power-factor band (for the Belvior
  defaults: 164 inverters, cos φ 0.9162–0.9181; the worksheet's goal-seeked
  0.918 falls inside this band).
- **Dynamic rows** — add or remove transformer groups and loss sources instead
  of a fixed layout with empty blocks.
- **Capacitor bank corrected** — a capacitor bank now *reduces* the reactive
  power the inverters must supply (the worksheet added it to the demand).
- **Validation** — a live pass/fail grid-delivery check, plus an over-sizing
  hint when the chosen power factor needs more inverters than the minimum.
- **Exposed assumptions** — the 1.10 design margin hard-coded in the worksheet
  formula is now an editable input.
- **Visuals** — a live power triangle (P/Q/S with φ) and a reactive-demand
  breakdown chart.
- **Scenarios** — inputs autosave in the browser; export/import JSON to archive
  or share; print-ready report layout; light and dark themes.
