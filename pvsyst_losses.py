# -*- coding: utf-8 -*-
"""PVsyst detailed-losses calculator.

Computes every loss item of the PVsyst "Detailed Losses" dialog and an
approximate annual loss diagram (waterfall) from GlobHor to E_Grid.
PVsyst itself runs an hourly simulation; this module uses
production-weighted annual averages, so the diagram is an estimate
(typically within 1-2 % of the simulation) while the individual
parameter values (Uc, soiling, mismatch, ohmic at STC, ...) are exactly
what you type into PVsyst.

Same equations as pvsyst_losses_calculator.html (the web UI).
"""

from dataclasses import dataclass, field

RHO = {"cu": 0.0172, "al": 0.0282}  # Ohm.mm^2/m at 20 degC


def cell_temperature(t_amb, g_inc, uc=20.0, uv=0.0, wind=1.5,
                     alpha=0.9, eta=0.21):
    """PVsyst U-value thermal model: Tcell = Tamb + G*alpha*(1-eta)/U."""
    u = uc + uv * wind
    return t_amb + (g_inc * alpha * (1.0 - eta) / u if u > 0 else 0.0)


def thermal_loss_pct(t_amb, g_inc, gamma_pmpp=0.34, **kw):
    """Average thermal loss in % (gamma entered as positive %/degC)."""
    return gamma_pmpp * (cell_temperature(t_amb, g_inc, **kw) - 25.0)


def soiling_loss_pct(rate_pct_per_day, days_between_cleaning):
    """Average soiling loss from a sawtooth build-up model.

    Soiling accumulates linearly at `rate_pct_per_day` and is reset by
    each cleaning or significant rain every `days_between_cleaning`.
    Returns (average_pct, peak_pct); the average is the PVsyst value.
    Typical rates (%/day): rural 0.02, suburban 0.04, urban/agricultural
    0.08, desert 0.15, heavy dust/industrial 0.25.
    """
    peak = min(rate_pct_per_day * days_between_cleaning, 50.0)
    return peak / 2.0, peak


def dc_ohmic_stc_pct(length_m, section_mm2, n_modules, vmp, imp,
                     material="cu", main_length_m=0.0, main_section_mm2=35.0,
                     n_strings=1, main_material="al"):
    """DC wiring loss fraction at STC (%), string cable + optional main cable.

    String segment: R = rho*2L/S carrying Imp; main DC cable (combiner box
    to inverter) carries n_strings*Imp. Loss per segment = I*R/Vstring,
    summed. This is the value PVsyst asks for; PVsyst applies its own
    quadratic scaling with current over the year.
    """
    v_string = vmp * n_modules
    if v_string <= 0:
        return 0.0
    r_str = RHO[material] * 2.0 * length_m / section_mm2
    loss = 100.0 * imp * r_str / v_string
    if main_length_m > 0:
        r_main = RHO[main_material] * 2.0 * main_length_m / main_section_mm2
        loss += 100.0 * max(n_strings, 1) * imp * r_main / v_string
    return loss


def ac_ohmic_pct(p_ac_kw, length_m, section_mm2, v_ll=400.0,
                 cos_phi=1.0, material="cu"):
    """Three-phase AC line loss at nominal power (%)."""
    if p_ac_kw <= 0:
        return 0.0
    r = RHO[material] * length_m / section_mm2          # per phase, one way
    i = p_ac_kw * 1000.0 / (3 ** 0.5 * v_ll * cos_phi)
    return 100.0 * 3.0 * i * i * r / (p_ac_kw * 1000.0)


def mv_line_loss_pct(p_ac_kw, length_m, section_mm2, v_kv=33.0,
                     cos_phi=1.0, material="al"):
    """Three-phase MV line loss (%) after the step-up transformer.

    Same formula as the LV side at the MV voltage; at MV the current is
    small, so this is usually only noticeable on long lines/large plants.
    """
    return ac_ohmic_pct(p_ac_kw, length_m, section_mm2,
                        v_ll=v_kv * 1000.0, cos_phi=cos_phi,
                        material=material)


def module_quality_default_pct(tol_low_pct, tol_high_pct):
    """PVsyst default module-quality loss: quarter of the tolerance spread.

    Negative result = gain (e.g. 0/+3 % sorting -> -0.75 %).
    """
    return -(tol_low_pct + tol_high_pct) / 4.0


def transformer_annual_pct(e_ac_kwh, p_iron_kw, p_copper_kw, p_nom_ac_kw,
                           load_factor=0.55):
    """Transformer annual loss %: iron runs 8760 h, copper scales ~quadratic."""
    if e_ac_kwh <= 0:
        return 0.0
    iron = p_iron_kw * 8760.0 / e_ac_kwh * 100.0
    copper = p_copper_kw / p_nom_ac_kw * load_factor * 100.0 if p_nom_ac_kw > 0 else 0.0
    return iron + copper


@dataclass
class SystemLosses:
    """All inputs of the PVsyst detailed-losses cascade (annual, %)."""
    # system & site
    pnom_kwp: float = 100.0
    glob_hor: float = 2000.0          # kWh/m2/yr
    transposition_pct: float = 15.0   # GlobInc gain over GlobHor
    eta_module: float = 0.21
    gamma_pmpp: float = 0.34          # %/degC (positive = drop above 25 degC)
    # irradiance losses
    far_shading: float = 0.0
    near_shading: float = 1.5
    iam: float = 2.5
    soiling: float = 3.0
    # thermal operating point (production-weighted averages)
    uc: float = 20.0
    uv: float = 0.0
    wind: float = 1.5
    t_amb: float = 25.0
    g_inc_avg: float = 600.0          # W/m2
    # array losses
    irradiance_level: float = 0.6
    module_quality: float = -0.75     # negative = gain
    lid: float = 2.0
    mismatch: float = 2.0
    strings_mismatch: float = 0.15
    dc_ohmic_stc: float = 1.5
    dc_duty_factor: float = 0.53      # annual quadratic-scaling factor
    # inverter
    inverter_euro_eff: float = 98.0
    clipping: float = 0.5
    threshold: float = 0.02
    # AC side & system
    ac_ohmic: float = 0.5
    transformer: float = 0.0          # annual %, use transformer_annual_pct()
    mv_line: float = 0.0              # %, use mv_line_loss_pct()
    auxiliaries: float = 0.3
    unavailability: float = 2.0
    curtailment: float = 0.0
    ageing_rate: float = 0.4          # %/yr
    year: int = 1                     # ageing loss = rate * (year - 1)

    def cascade(self):
        """Return (steps, summary): the annual loss waterfall.

        steps: list of (name, loss_pct, energy_after_kwh); irradiance-domain
        steps carry the running irradiance in kWh/m2 instead of energy.
        """
        steps = []
        irr = self.glob_hor * (1.0 + self.transposition_pct / 100.0)
        glob_inc = irr
        steps.append(("Transposition", -self.transposition_pct, irr))
        for name, pct in (("Far shading", self.far_shading),
                          ("Near shadings", self.near_shading),
                          ("IAM", self.iam),
                          ("Soiling", self.soiling)):
            irr *= 1.0 - pct / 100.0
            steps.append((name, pct, irr))
        glob_eff = irr

        thermal = thermal_loss_pct(self.t_amb, self.g_inc_avg,
                                   gamma_pmpp=self.gamma_pmpp, uc=self.uc,
                                   uv=self.uv, wind=self.wind,
                                   eta=self.eta_module)
        e = e_nom = glob_eff * self.pnom_kwp
        energy_steps = (
            ("Irradiance level", self.irradiance_level),
            ("Temperature", thermal),
            ("Module quality", self.module_quality),
            ("LID", self.lid),
            ("Mismatch", self.mismatch),
            ("Strings mismatch", self.strings_mismatch),
            ("DC ohmic (annual)", self.dc_ohmic_stc * self.dc_duty_factor),
            ("Inverter efficiency", 100.0 - self.inverter_euro_eff),
            ("Clipping", self.clipping),
            ("Threshold", self.threshold),
            ("AC ohmic", self.ac_ohmic),
            ("Transformer", self.transformer),
            ("MV line", self.mv_line),
            ("Auxiliaries", self.auxiliaries),
            ("Unavailability", self.unavailability),
            ("Curtailment", self.curtailment),
            ("Ageing", self.ageing_rate * max(self.year - 1, 0)),
        )
        for name, pct in energy_steps:
            e *= 1.0 - pct / 100.0
            steps.append((name, pct, e))

        summary = {
            "glob_inc": glob_inc,
            "glob_eff": glob_eff,
            "e_nom_kwh": e_nom,
            "e_grid_kwh": e,
            "specific_yield": e / self.pnom_kwp if self.pnom_kwp else 0.0,
            "pr": e / (self.pnom_kwp * glob_inc) if self.pnom_kwp * glob_inc else 0.0,
            "thermal_loss_pct": thermal,
            "t_cell": cell_temperature(self.t_amb, self.g_inc_avg, uc=self.uc,
                                       uv=self.uv, wind=self.wind,
                                       eta=self.eta_module),
        }
        return steps, summary


if __name__ == "__main__":
    sys_losses = SystemLosses()
    steps, s = sys_losses.cascade()
    print(f"{'Loss item':<22}{'loss %':>8}   remaining")
    print("-" * 48)
    print(f"{'GlobHor':<22}{'':>8}   {sys_losses.glob_hor:10,.0f} kWh/m2")
    for name, pct, after in steps:
        unit = "kWh/m2" if name in ("Transposition", "Far shading",
                                    "Near shadings", "IAM", "Soiling") else "kWh"
        sign = "+" if name == "Transposition" or pct < 0 else "-"
        print(f"{name:<22}{sign}{abs(pct):>6.2f}%   {after:10,.0f} {unit}")
    print("-" * 48)
    print(f"E_Grid  = {s['e_grid_kwh']:,.0f} kWh/yr")
    print(f"Yield   = {s['specific_yield']:,.0f} kWh/kWp/yr")
    print(f"PR      = {100 * s['pr']:.1f} %")
    print(f"T cell  = {s['t_cell']:.1f} degC  (thermal loss {s['thermal_loss_pct']:.2f} %)")
