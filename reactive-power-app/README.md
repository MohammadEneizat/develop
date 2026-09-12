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
4. **Inverter fleet** — no power-factor knob: each inverter dispatches the
   active power the plant needs, (grid limit + losses) ÷ count, and its
   reactive capability follows from that loading. Enter the plant's inverter
   count or use the recommended count — the smallest fleet covering both the
   active delivery and the reactive demand.
5. **Inverter P–Q capability** *(new, not in the worksheet)* — the datasheet's
   Q(t)-mode capability table, editable in place, rendered as a P–Q diagram.
   Pre-filled with the **Sungrow SC210HX** (231 kVA / 210 kW) from its TÜV
   Rheinland VDE-AR-N 4110/4120/4130 test report (No. 968/GI 2194.01/25); the
   circle model reproduces the report's Tables 4-5/4-6 and Figures 4-2..4-9
   exactly.
6. **Grid-code compliance diagrams** *(new, not in the worksheet)* — the two
   assessment curves of a G99 Type C study: the **V–Q diagram** (requirement
   polygon vs the plant's reactive capability at each voltage *while delivering
   full active power* — active power is the priority and is never curtailed for
   reactive, so the envelope narrows where the inverter is current-limited at
   low voltage) with the A/B/E/F corner points, and the **P–Q diagram** at
   nominal voltage. A corner-point table reports the required and available
   reactive power per point.

The engine reproduces the workbook's intermediate values exactly (MVA rating
55.58, MVAr demand 23.60, transformer demand, losses 1.742 MW, apparent power
59.43 MVA). The **recommended inverter count** now reflects grid-code
compliance across the voltage range at full active power, so it exceeds the
worksheet's reactive-only count — 174 for the Belvior defaults with the
capability table (173 with the circle model) — with the plant delivering the
full 52.8 MW grid limit.

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
  Custom), shows the clause summary, and syncs the plant power factor.
- **G99-style compliance diagrams (Step 7)** — the two assessment curves of a
  professional G99 Type C reactive power study:
  - **V–Q diagram at Registered Capacity**: the requirement polygon (for G99
    the true asymmetric hexagon of Fig. 13.13 — full lagging/export Q at
    0.95–1.00 p.u. tapering to zero at 1.05, full leading/absorption at
    1.00–1.05 tapering to zero at 0.95) against the plant's capability
    envelope over the voltage range, both Q directions, with the A/B/E/F
    corner load-flow points marked.
  - **P–Q diagram at nominal voltage**: the G99 Fig. 13.14 envelope — full
    ±Q from 20% output, the DNO-discretion lead-side relief triangle between
    20–50%, and the ±5% tolerance stub below MSOL — against the plant
    capability loop.
  - A **corner-point table** (the A/B/E/F cases of the study's Table 3-1) in
    the results rail with per-point pass/fail.
  - Calculation convention matched to the study: inverters dispatch the
    active power actually needed — (grid limit + losses) ÷ count — so surplus
    inverters free reactive headroom; export capability is net of transformer
    consumption while absorption is aided by it; the capacitor bank counts
    for export only; inverter capability is taken as symmetric. The app draws the requirement's P–Q envelope and V–Q profile,
  overlays the V-dependent requirement on the voltage sweep (replacing the
  flat demand line), and adds a **Grid code compliance** chart in the results:
  plant reactive capability at the POI (net of transformer consumption,
  evaluated at the true per-inverter dispatch for each output level) against
  the requirement across 0–100 % output, with shortfall shading and a
  covered/not-covered verdict.

- **Live recalculation** — every result updates as you type.
- **Recommended inverter count (active-power priority)** — replaces Excel's
  manual *Goal Seek* step entirely: the app computes the smallest fleet that
  delivers full active power AND meets the reactive requirement across the
  voltage range, with active power never curtailed for reactive (Belvior
  defaults: 174 with the capability table, 173 with the circle model). The
  equivalent cos φ at dispatch is reported as an output.
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
- **Inverter regulated voltage** — an optional control for the inverter's own
  AC terminal voltage. Left blank, the capability table is read at the
  connection-point voltage being assessed (a conservative single-voltage
  screen). Set it (e.g. 1.00 p.u.) when the inverter bus is held by the MV/LV
  transformer and the main transformer's on-load tap changer, so the reactive
  capability is read at the inverter terminals rather than derated by a
  depressed POI voltage — as a detailed load-flow (PowerFactory) models it.
  This is the knob that reconciles the screening count with a detailed study:
  for the Infraleuna 48 MW / VDE-AR-N 4110 case, blank gives 164 inverters
  while **0.97 p.u. gives 160, matching the PowerFactory result** (the 0.95 p.u.
  export corner is the binding constraint).
- **Capacitor bank corrected** — a capacitor bank now *reduces* the reactive
  power the inverters must supply (the worksheet added it to the demand).
- **Validation** — a live pass/fail grid-delivery check, plus an over-sizing
  hint when the chosen power factor needs more inverters than the minimum.
- **Exposed assumptions** — the 1.10 design margin hard-coded in the worksheet
  formula is now an editable input.
- **Visuals** — a live power triangle (P/Q/S with φ) and a reactive-demand
  breakdown chart.
- **Scenarios** — inputs autosave in the browser; export/import JSON to archive
  or share; light and dark themes.
- **One-click PDF report** — *Download PDF report* builds a professional
  multi-page A4 study document (cover, executive summary, inputs & assumptions,
  grid-code requirement, sizing, inverter P–Q capability, compliance,
  conclusion) with jsPDF and saves it straight to the device — no browser print
  dialog. Text is native and selectable, tables are laid out with jsPDF-AutoTable,
  and the charts are embedded from the live diagrams at high resolution;
  pagination is controlled in code so a figure or table never splits across a
  page. jsPDF and its AutoTable plugin are bundled in the single HTML file, so
  it still works fully offline.
