# Reactive Power Compensation Sizing App

An interactive web app built from the `Reactive_Power_Compensation_Belvior.xlsx`
worksheet. It sizes the reactive power compensation of a utility-scale solar PV
plant, checks the design against published grid-code requirements, and
generates a professional study report — following the structure of a G99
Type C load-flow and reactive power study.

**Run it:** open `index.html` in any browser. It is fully self-contained —
no build step, no dependencies, works offline. Inputs autosave in the browser;
scenarios can be exported/imported as JSON, and two complete examples are
built in: **Belvior** (the original worksheet) and **Brecks Solar Farm** (the
public values of a real G99 Type C study — 32.7 MW RC, 106 × 352 kVA
inverters with their Q(t) capability table; impedances and losses are
typical assumptions).

## Workflow

| Step | What it does |
|---|---|
| 1 — Initial sizing | Grid injection limit and power factor → plant MVA rating and grid MVAr demand. Select a **grid code** (G99, VDE-AR-N 4110/4120, IEEE 1547-2018 Cat B, NER S5.2.5.1, ENTSO-E RfG, generic, or custom); its published P–Q and V–Q requirement envelopes are drawn in study-figure style. |
| 2 — Transformers | Reactive consumption per group (`Q = qty × rating × Z%`) with an editable design margin; dynamic rows. |
| 3 — Losses | PVsyst loss fractions applied to the grid limit; dynamic rows. |
| 4 — Inverters | Apparent power, operating PF, capacitor bank, inverter count (blank = auto-size to meet both reactive demand and delivery), reactive capability (table > manual kVAr > √(S²−P²)), and a built-in **Goal Seek** that finds the minimum inverter count and the feasible PF band. |
| 5 — P–Q capability | The manufacturer's Q(t)-mode capability table (% of rated kVA per voltage row and loading column, blank = N/A), rendered as the inverter P–Q capability diagram with the design operating point. |
| 6 — Voltage sweep | Plant reactive capability at each grid voltage at Registered-Capacity dispatch, against the voltage-tapered grid-code requirement. Where the table does not permit the dispatch loading, active power is backed off to the maximum permitted point and the reactive capability there is used (flagged as P-curtailment). |
| 7 — Compliance diagrams | The two assessment curves of a G99 Type C study: the **V–Q diagram** at Registered Capacity (requirement polygon — for G99 the true asymmetric hexagon — vs the plant capability envelope, with A/B/E/F corner points) and the **P–Q diagram** at nominal voltage (envelope with lead-relief triangle and tolerance stub vs the capability loop). |

The results rail shows the final sizing with a live power triangle, the
reactive-demand breakdown, the grid delivery check, and the corner-point
compliance table. **Generate PDF report** composes a print-ready study
document (cover, executive summary, inputs & assumptions, requirement
figures, results, compliance diagrams, verdict, conclusion) — use the
browser's "Save as PDF".

## Modelling conventions

- Inverters dispatch the active power actually needed — (grid limit + losses)
  ÷ count — so surplus inverters free reactive headroom (G99 study convention).
- Inverter reactive capability is symmetric; voltage capability is
  interpolated linearly between capability-table rows, conservatively across
  N/A gaps.
- Export capability at the POI is net of transformer consumption; absorption
  is aided by it; the capacitor bank counts for export only.
- Grid-code presets are typical published values (sources below) — always
  confirm against the applicable interconnection agreement. The app is an
  analytic screening tool, not a substitute for a network load-flow study.

## Grid-code sources

- **UK — ENA G99 / GB Grid Code**: [ECC.6.3.2 guidance (NESO)](https://www.neso.energy/document/202461/download),
  [G99 reactive power overview](https://aurora-power.co.uk/g99-reactive-power/)
- **Germany — VDE-AR-N 4110 (MV)**: [summary](https://www.vde.com/resource/blob/1708464/47dedcd3571bc7fdbc29fd3704dce88a/tcr-medium-voltage-en-data.pdf)
- **Germany — VDE-AR-N 4120 (HV)**: [summary](https://www.vde.com/resource/blob/1674518/0f43075f390bc86a0d51a74b805c683e/tar-hs-download-en-data.pdf)
- **USA — IEEE 1547-2018 Category B**: [NREL highlights](https://docs.nrel.gov/docs/fy20osti/75436.pdf)
- **Australia — NER S5.2.5.1**: [clause text](https://energy-rules.aemc.gov.au/ner/477/272957)

## Verification

The calculation engine reproduces the original workbook exactly (MVA rating
55.58, MVAr demand 23.60, losses 1.742 MW, 164 inverters, 52.908 MW delivered
with the capability table off), and the grid-code envelopes were verified
against the published clause values (e.g. G99: Q = ±10.8 MVAr at a 32.7 MW
Registered Capacity). Chart palettes are colour-vision-deficiency checked in
both light and dark themes.

## Repository contents

- `index.html` — the app (single file).
- `excel-tool/` — a standalone Excel workbook version of the tool
  (`Reactive_Power_Compensation_Tool.xlsx`, pure formulas, no macros) and its
  Python generator; verified by headless LibreOffice recalculation against
  the app.
