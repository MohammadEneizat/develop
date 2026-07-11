# PVsyst Detailed Losses Calculator

A tool that computes every loss item requested by PVsyst's **Detailed Losses** dialog, with an estimated annual loss diagram from `GlobHor` down to `E_Grid`.

## Files

| File | Description |
|---|---|
| `pvsyst_losses_calculator.html` | Interactive web app — open it directly in any browser, no installation. Light/dark theme, copy values or download them as CSV. |
| `pvsyst_losses.py` | The same equations as a Python module for programmatic use — `python3 pvsyst_losses.py` prints the loss diagram. |

## Loss items covered

- **Irradiance losses**: far shading (horizon), near shadings, incidence angle (IAM, ASHRAE model), soiling — direct % or a **soiling estimator** (site-environment presets, sawtooth build-up: average loss = accumulation rate × cleaning interval / 2).
- **Thermal loss**: PVsyst's U-value model — `Tcell = Tamb + G·α·(1−η)/(Uc + Uv·v)` with mounting presets (free-standing 29, semi-integrated 20, insulated 15 W/m²K).
- **Array losses**: low-light irradiance level, module quality (quarter-of-tolerance rule), LID, module mismatch, strings voltage mismatch, ageing.
- **DC ohmic loss**: direct % at STC or a **two-segment cable calculator** — string cables (carrying Imp) plus the main DC cable from combiner box to inverter (carrying n strings × Imp), `R = ρ·2L/S`, copper/aluminium — with the effective annual loss.
- **Inverter**: European efficiency, overpower clipping with a DC/AC ratio indicator, power threshold.
- **AC side & MV**: LV cable loss (direct % or 3-phase calculator), MV step-up transformer (iron loss over 8760 h + quadratic copper loss), and an **MV line calculator** (3-phase loss at the medium-voltage level to the grid connection point).
- **Plant level**: auxiliaries, unavailability, grid curtailment.

## Outputs

- Each parameter value ready to enter in PVsyst, with its location in the program (copyable/downloadable table).
- Annual loss diagram: `GlobHor → GlobEff → E_nom → E_Array → E_Inv → E_Grid`.
- Indicators: annual energy `E_Grid`, specific yield (kWh/kWp), performance ratio **PR**.

## Methodology note

PVsyst runs a full hourly simulation, while this tool uses production-weighted annual averages — so the diagram is an estimate (usually within ±1–2%). The individual parameter values (Uc, soiling, mismatch, DC ohmic at STC, …) are exactly what you enter in the program.
