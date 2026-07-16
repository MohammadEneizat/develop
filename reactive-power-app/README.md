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
5. **Inverter P–Q capability** *(new, not in the worksheet)* — the datasheet's
   Q(t)-mode capability table, editable in place, rendered as a P–Q diagram.
6. **Reactive capability vs grid voltage** *(new, not in the worksheet)* — the
   plant's reactive capability evaluated across a grid-voltage band
   (default 0.80–1.15 p.u., editable). With the capability table in use, each
   level reads the table (interpolated, clamped at the edges); otherwise a
   current-limit model applies (`S(V) = V × S_rated` below nominal, rated
   above, P-priority: `q(V) = √(S(V)² − p²)`). Each level gets a pass/fail
   verdict against the reactive demand, with active-power-curtailment
   flagging, plus a capability curve chart with hover details.

The engine was verified against the workbook's cached values: all intermediate
and final results (MVA rating, MVAr demand, transformer demand, losses,
apparent power, inverter count 164, delivered power 52.908 MW) match exactly.

## Improvements over the spreadsheet

- **Grid code requirements & compliance** — select a named grid code in
  Step 1 from a built-in database of published requirements, all normalised to
  one editable envelope model (Q at Pmax, no-requirement / full-Q output
  thresholds with a linear ramp, and a V–Q voltage band with tapers):
  - **United Kingdom — ENA G99 / GB Grid Code (Type C/D PPM)**: 0.95 lead/lag
    at Registered Capacity, full range down to 50% output, linear reduction
    below, none under 20% ([Grid Code ECC.6.3.2 guidance](https://www.neso.energy/document/202461/download),
    [G99 reactive power overview](https://aurora-power.co.uk/g99-reactive-power/))
  - **Germany — VDE-AR-N 4110 (MV)**: cos φ 0.95 above 20% of installed
    capacity, control range 0.925–1.075 p.u.
    ([VDE-AR-N 4110 summary](https://www.vde.com/resource/blob/1708464/47dedcd3571bc7fdbc29fd3704dce88a/tcr-medium-voltage-en-data.pdf),
    [practical guide](https://www.kbr.de/en/aktuelles/vde-ar-n-4110-reactive-power-behavior-explained-in-a-practical-way/))
  - **Germany — VDE-AR-N 4120 (HV)**: cos φ 0.925 variant (three
    TSO-selectable variants exist)
    ([VDE-AR-N 4120 summary](https://www.vde.com/resource/blob/1674518/0f43075f390bc86a0d51a74b805c683e/tar-hs-download-en-data.pdf))
  - **USA — IEEE 1547-2018 Category B**: inject/absorb 44% of nameplate kVA
    (≈0.90 PF at rated), full capability above 20% of rated power
    ([NREL highlights of IEEE 1547-2018](https://docs.nrel.gov/docs/fy20osti/75436.pdf))
  - **Australia — NER S5.2.5.1 (Automatic access)**: ±0.395 × rated active
    power at any output level
    ([NER clause S5.2.5.1](https://energy-rules.aemc.gov.au/ner/477/272957))
  - **EU — ENTSO-E RfG**: typical Type C/D national implementation
    (Regulation 2016/631 leaves exact envelopes to each TSO)
  - Generic fixed-PF presets and **Custom**.

  Selecting a code fills the parameters (still editable — editing switches to
  Custom), shows the clause summary, and syncs the plant power factor. The app draws the requirement's P–Q envelope and V–Q profile,
  overlays the V-dependent requirement on the voltage sweep (replacing the
  flat demand line), and adds a **Grid code compliance** chart in the results:
  plant reactive capability at the POI (net of transformer consumption,
  evaluated at the true per-inverter dispatch for each output level) against
  the requirement across 0–100 % output, with shortfall shading and a
  covered/not-covered verdict.

- **Live recalculation** — every result updates as you type.
- **Built-in Goal Seek** — replaces Excel's manual *Data ▸ What-If Analysis ▸
  Goal Seek* step. It solves analytically for the minimum inverter count that
  meets both the active requirement (grid limit + losses) and the reactive
  requirement, and reports the full feasible power-factor band (for the Belvior
  defaults: 164 inverters, cos φ 0.9162–0.9181; the worksheet's goal-seeked
  0.918 falls inside this band).
- **Dynamic rows** — add or remove transformer groups and loss sources instead
  of a fixed layout with empty blocks.
- **Inverter P–Q capability table & diagram** — enter the manufacturer's
  Q(t)-mode table directly (max reactive power as % of rated kVA, per grid
  voltage row, per active-loading column; empty cell = N/A). The app draws the
  inverter P–Q capability diagram from it — symmetric capacitive/inductive
  curves per voltage (identical rows grouped like the datasheet legend), with
  the design operating point plotted on it. When enabled, the table also
  drives the sizing (capability at the 1.00 Vn row and dispatched loading),
  the Goal Seek (numeric scan, since capability varies with PF), and the
  voltage sweep (interpolated between rows and loadings; N/A regions are
  flagged as curtailed). When disabled, capability falls back to the manual
  kVAr field or the √(S² − P²) derivation. If the stated Q exceeds √(S² − P²), the
  app warns and assumes an effective apparent limit for the voltage sweep.
- **Controllable inverter count** — leave the count blank to auto-size (the
  count that meets both the reactive demand and the delivery requirement at
  the chosen PF), or fix it to the number the plant actually has. All downstream results (delivered power, reactive
  coverage, the voltage sweep) then use the fixed count, shortfalls in either
  active or reactive terms are flagged, and Goal Seek solves the feasible
  power-factor band at that count (or reports the minimum viable count when
  none exists).
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
