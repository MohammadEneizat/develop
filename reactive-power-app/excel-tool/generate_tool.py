#!/usr/bin/env python3
"""Generates Reactive_Power_Compensation_Tool.xlsx — a standalone Excel
version of the reactive power sizing app: full calculation chain with live
formulas, a grid-code requirement database with dropdown selection, an
editable inverter P-Q capability table with interpolation, and a compliance
sheet with V-Q / P-Q charts. No macros; plain formulas only."""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.utils import get_column_letter

# ---------- palette ----------
HEAD = PatternFill("solid", fgColor="1C5CAB")
INPUT = PatternFill("solid", fgColor="FFF3CC")   # editable inputs
CALC = PatternFill("solid", fgColor="EEF1F4")    # computed
RESULT = PatternFill("solid", fgColor="E6F4E6")  # key results
HEADF = Font(bold=True, color="FFFFFF")
BOLD = Font(bold=True)
THIN = Border(*[Side(style="thin", color="C9CFD6")] * 4)


def style(ws, cell, fill=None, bold=False, num=None, wrap=False):
    c = ws[cell]
    if fill is not None:
        c.fill = fill
    if bold:
        c.font = BOLD
    if num:
        c.number_format = num
    if wrap:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    c.border = THIN
    return c


def section(ws, cell, text):
    ws[cell] = text
    ws[cell].font = HEADF
    ws[cell].fill = HEAD


wb = openpyxl.Workbook()

# =============================== README ===============================
rd = wb.active
rd.title = "README"
rd.column_dimensions["A"].width = 110
rows = [
    ("REACTIVE POWER COMPENSATION SIZING TOOL", True),
    ("", False),
    ("A standalone Excel version of the reactive power sizing app. Sheets:", False),
    ("  1. Sizing — the calculation chain: grid demand, transformer consumption, losses, inverter sizing, checks.", False),
    ("  2. GridCodes — database of published grid-code reactive requirements; pick one from the dropdown.", False),
    ("  3. InverterPQ — the manufacturer's Q(t)-mode capability table (%% of rated kVA per voltage row and loading).", False),
    ("  4. Compliance — V-Q at Registered Capacity and P-Q at nominal voltage vs the selected grid code, with charts.", False),
    ("", False),
    ("Colour key:  yellow = input cells,  grey = calculated,  green = key results.", False),
    ("", False),
    ("Notes:", True),
    ("  - Inverter count: leave the manual-count cell blank to auto-size (meets both reactive and delivery needs).", False),
    ("  - Reactive capability precedence: capability table (if 'Use table' = Yes) > manual kVAr override > sqrt(S^2-P^2).", False),
    ("  - Compliance dispatches inverters at (grid limit + losses) / count, as in a G99 Type C study.", False),
    ("  - Export capability is net of transformer consumption; absorption is aided by it; capacitor bank exports only.", False),
    ("  - Grid-code presets are typical published values - always confirm against your interconnection agreement.", False),
    ("  - This tool is an analytic screening aid, not a substitute for a network load-flow study.", False),
]
for i, (t, b) in enumerate(rows, start=1):
    rd[f"A{i}"] = t
    if b:
        rd[f"A{i}"].font = BOLD

# =============================== SIZING ===============================
sz = wb.create_sheet("Sizing")
for col, w in zip("ABCDE", (46, 14, 10, 14, 12)):
    sz.column_dimensions[col].width = w

section(sz, "A1", "PROJECT")
sz["A2"] = "Project name"
sz["B2"] = "Belvior"
style(sz, "B2", INPUT)

section(sz, "A4", "STEP 1 — INITIAL SIZING")
sz["A5"] = "Grid injection limit / Registered Capacity"
sz["B5"] = 52.8
sz["C5"] = "MW"
style(sz, "B5", INPUT)
sz["A6"] = "Power factor at grid"
sz["B6"] = 0.95
sz["C6"] = "cos phi"
style(sz, "B6", INPUT)
sz["A7"] = "MVA rating of plant"
sz["B7"] = "=B5/B6"
sz["C7"] = "MVA"
style(sz, "B7", CALC, num="0.00")
sz["A8"] = "MVAr demand (grid PF)"
sz["B8"] = "=SQRT(B7^2-B5^2)"
sz["C8"] = "MVAr"
style(sz, "B8", CALC, num="0.00")

section(sz, "A10", "STEP 2 — TRANSFORMER REACTIVE CONSUMPTION")
for j, h in enumerate(["Group", "Qty", "Rating (kVA)", "Impedance (%)", "Q (kVAr)"]):
    cell = f"{get_column_letter(j+1)}11"
    sz[cell] = h
    sz[cell].font = BOLD
xmers = [
    ("TS Block 1", 3, 10164, 9.5),
    ("TS Block 2", 4, 7260, 9.5),
    ("Auxiliary transformer (MCR)", 1, 500, 4.5),
    ("", None, None, None),
    ("", None, None, None),
    ("", None, None, None),
]
for i, (n, q, kva, z) in enumerate(xmers):
    r = 12 + i
    sz[f"A{r}"] = n
    if q is not None:
        sz[f"B{r}"], sz[f"C{r}"], sz[f"D{r}"] = q, kva, z
    for col in "ABCD":
        style(sz, f"{col}{r}", INPUT)
    sz[f"E{r}"] = f"=IF(COUNT(B{r}:D{r})=3,B{r}*C{r}*D{r}/100,0)"
    style(sz, f"E{r}", CALC, num="0.0")
sz["A18"] = "Design margin on transformer demand"
sz["B18"] = 10
sz["C18"] = "%"
style(sz, "B18", INPUT)
sz["A19"] = "Transformer demand incl. margin"
sz["B19"] = "=SUM(E12:E17)/1000*(1+B18/100)"
sz["C19"] = "MVAr"
style(sz, "B19", CALC, num="0.00")
sz["A20"] = "TOTAL REACTIVE DEMAND"
sz["B20"] = "=B8+B19"
sz["C20"] = "MVAr"
style(sz, "B20", RESULT, bold=True, num="0.00")

section(sz, "A22", "STEP 3 — INTERNAL SYSTEM LOSSES")
losses = [("AC cable loss", 1.0), ("Auxiliary system loss (string inverters)", 1.0),
          ("Transmission line loss", 0.3), ("Miscellaneous losses", 1.0)]
sz["A23"], sz["B23"], sz["C23"] = "Loss source", "Fraction (%)", "Loss (MW)"
for c in ("A23", "B23", "C23"):
    sz[c].font = BOLD
for i, (n, pct) in enumerate(losses):
    r = 24 + i
    sz[f"A{r}"] = n
    sz[f"B{r}"] = pct
    style(sz, f"B{r}", INPUT)
    sz[f"C{r}"] = f"=B{r}*$B$5/100"
    style(sz, f"C{r}", CALC, num="0.000")
sz["A28"] = "Total system losses"
sz["B28"] = "=SUM(C24:C27)"
sz["C28"] = "MW"
style(sz, "B28", CALC, num="0.000")
sz["A29"] = "Capacity to be considered"
sz["B29"] = "=B5+B28"
sz["C29"] = "MW"
style(sz, "B29", CALC, num="0.00")

section(sz, "A31", "STEP 4 — INVERTER CAPABILITY & COMPENSATION")
inv_rows = [
    ("Inverter apparent power", 363, "kVA", INPUT, None),
    ("PF at inverter level (use Data > What-If > Goal Seek on B45 or B46)", 0.918, "cos phi", INPUT, None),
    ("Active power / inverter", "=B32*B33", "kW", CALC, "0.0"),
    ("Reactive capability - derived sqrt(S^2-P^2)", "=SQRT(B32^2-B34^2)", "kVAr", CALC, "0.0"),
    ("Reactive capability - manual override (optional)", None, "kVAr", INPUT, None),
    ("Reactive capability - from InverterPQ table (at PF loading)", "=InverterPQ!B16", "kVAr", CALC, "0.0"),
    ("Q per inverter USED", '=IF(InverterPQ!B1="Yes",B37,IF(ISNUMBER(B36),B36,B35))', "kVAr", CALC, "0.0"),
    ("Capacitor bank", 0, "MVAr", INPUT, None),
    ("Q for inverters (after cap bank)", "=MAX(0,B20-B39)", "MVAr", CALC, "0.00"),
    ("Manual inverter count (blank = auto)", None, "nos.", INPUT, None),
    ("Required inverters - reactive", "=IF(B38>0,ROUNDUP(B40*1000/B38,0),0)", "nos.", CALC, "0"),
    ("Required inverters - active delivery", "=ROUNDUP(B29*1000/B34,0)", "nos.", CALC, "0"),
    ("Inverters in design", "=IF(ISNUMBER(B41),B41,MAX(B42,B43))", "nos.", RESULT, "0"),
    ("Power delivered to grid (net of losses)", "=B44*B34/1000-B28", "MW", RESULT, "0.00"),
    ("Reactive power compensated", "=B44*B38/1000+B39", "MVAr", RESULT, "0.00"),
    ("Delivery check (>= grid limit)", '=IF(B45>=B5-0.000001,"PASS","FAIL")', "", RESULT, None),
    ("Reactive check (>= total demand)", '=IF(B46>=B20-0.000001,"PASS","FAIL")', "", RESULT, None),
]
for i, (label, val, unit, fill, num) in enumerate(inv_rows):
    r = 32 + i
    sz[f"A{r}"] = label
    if val is not None:
        sz[f"B{r}"] = val
    sz[f"C{r}"] = unit
    style(sz, f"B{r}", fill, num=num)

# =============================== GRIDCODES ===============================
gcs = wb.create_sheet("GridCodes")
widths = {"A": 10, "B": 52, "C": 9, "D": 7, "E": 8, "F": 10, "G": 7, "H": 7,
          "I": 9, "J": 9, "K": 6, "L": 9, "M": 9, "N": 90}
for col, w in widths.items():
    gcs.column_dimensions[col].width = w
gcs["A1"] = "Selected grid code:"
gcs["A1"].font = BOLD
gcs["B1"] = "United Kingdom - ENA G99 / GB Grid Code (Type C/D PPM)"
style(gcs, "B1", INPUT)
headers = ["Key", "Name", "Q/Pmax", "PF", "pMin %", "pFullLag %", "Relief", "Stub",
           "VFullLo", "VFullHi", "Asym", "VZeroLo", "VZeroHi", "Notes"]
for j, h in enumerate(headers):
    c = f"{get_column_letter(j+1)}3"
    gcs[c] = h
    gcs[c].font = HEADF
    gcs[c].fill = HEAD
codes = [
    ("gb_g99", "United Kingdom - ENA G99 / GB Grid Code (Type C/D PPM)", 0.329, 0.95, 20, 20, 1, 0.05, 0.95, 1.05, 1, 0.90, 1.10,
     "0.95 lead/lag at RC from 20% output (G99 13.5.5, Fig 13.13/13.14). Asymmetric V-Q; lead relief triangle 20-50% at DNO discretion; +/-5% band below 20%."),
    ("de_4110", "Germany - VDE-AR-N 4110 (medium voltage)", 0.329, 0.95, 20, 20, 0, 0, 0.95, 1.05, 0, 0.925, 1.075,
     "cos phi 0.95 under/overexcited above 20% of installed capacity; control range 0.925-1.075 pu."),
    ("de_4120", "Germany - VDE-AR-N 4120 (high voltage)", 0.411, 0.925, 20, 20, 0, 0, 0.95, 1.05, 0, 0.90, 1.10,
     "cos phi 0.925 variant (three TSO-selectable variants exist)."),
    ("us_1547b", "USA - IEEE 1547-2018 (Category B)", 0.44, 0.90, 20, 20, 0, 0, 0.95, 1.05, 0, 0.90, 1.10,
     "Inject/absorb 44% of nameplate kVA (~0.90 PF at rated); full capability above 20% of rated power."),
    ("au_ner", "Australia - NER S5.2.5.1 (Automatic access)", 0.395, 0.93, 0, 0, 0, 0, 0.95, 1.05, 0, 0.90, 1.10,
     "+/-0.395 x rated active power at any output level."),
    ("eu_rfg", "EU - ENTSO-E RfG (typical Type C/D implementation)", 0.329, 0.95, 20, 50, 0, 0, 0.95, 1.05, 0, 0.90, 1.10,
     "Regulation 2016/631 leaves envelopes to each TSO - typical national choice shown."),
    ("pf95", "Generic - fixed PF 0.95 lead/lag", 0.329, 0.95, 20, 20, 0, 0, 0.95, 1.05, 0, 0.90, 1.10, "Fixed PF, full Q above 20% output."),
    ("pf90", "Generic - fixed PF 0.90 lead/lag", 0.484, 0.90, 20, 20, 0, 0, 0.95, 1.05, 0, 0.90, 1.10, "Fixed PF, full Q above 20% output."),
]
for i, row in enumerate(codes):
    r = 4 + i
    for j, v in enumerate(row):
        c = f"{get_column_letter(j+1)}{r}"
        gcs[c] = v
        gcs[c].border = THIN
        if j == 13:
            gcs[c].alignment = Alignment(wrap_text=True, vertical="top")
dv = DataValidation(type="list", formula1="=$B$4:$B$11", allow_blank=False, showDropDown=False)
gcs.add_data_validation(dv)
dv.add(gcs["B1"])
gcs["A13"] = "Active parameters (looked up from the selected code):"
gcs["A13"].font = BOLD
active = ["Q/Pmax", "PF", "pMin %", "pFullLag %", "Relief", "Stub", "VFullLo", "VFullHi", "Asym", "VZeroLo", "VZeroHi"]
for j, name in enumerate(active):
    hc = f"{get_column_letter(j+2)}14"
    vc = f"{get_column_letter(j+2)}15"
    gcs[hc] = name
    gcs[hc].font = BOLD
    src_col = get_column_letter(j + 3)  # C..M
    gcs[vc] = f"=INDEX(${src_col}$4:${src_col}$11,MATCH($B$1,$B$4:$B$11,0))"
    style(gcs, vc, CALC)

# =============================== INVERTERPQ ===============================
pq = wb.create_sheet("InverterPQ")
pq.column_dimensions["A"].width = 34
for j in range(2, 14):
    pq.column_dimensions[get_column_letter(j)].width = 8
pq["A1"] = "Use capability table for sizing?"
pq["A1"].font = BOLD
pq["B1"] = "Yes"
style(pq, "B1", INPUT)
dv2 = DataValidation(type="list", formula1='"Yes,No"', allow_blank=False, showDropDown=False)
pq.add_data_validation(dv2)
dv2.add(pq["B1"])
pq["A3"] = "Max reactive power, % of rated kVA (blank = N/A, operation not permitted)"
pq["A3"].font = BOLD
pq["A4"] = "V (pu) \\ P loading (pu)"
pq["A4"].font = BOLD
plevels = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
for j, p in enumerate(plevels):
    c = f"{get_column_letter(2+j)}4"
    pq[c] = p
    pq[c].font = BOLD
    pq[c].fill = HEAD
    pq[c].font = HEADF
table = [
    (1.10, [60, 60, 60, 60, 60, 60, 60, 60, 60, 43.6, 0]),
    (1.05, [60, 60, 60, 60, 60, 60, 60, 60, 60, 43.6, 0]),
    (1.00, [60, 60, 60, 60, 60, 60, 60, 60, 60, 43.6, 0]),
    (0.95, [60, 60, 60, 60, 60, 60, 60, 60, 51.2, 30.4, None]),
    (0.90, [60, 60, 60, 60, 60, 60, 60, 56.6, 41.2, 0, None]),
    (0.85, [60, 60, 60, 60, 60, 60, 60, 48.2, 28.7, None, None]),
]
for i, (v, vals) in enumerate(table):
    r = 5 + i
    pq[f"A{r}"] = v
    style(pq, f"A{r}", INPUT, bold=True)
    for j, q in enumerate(vals):
        c = f"{get_column_letter(2+j)}{r}"
        if q is not None:
            pq[c] = q
        style(pq, c, INPUT)


def interp_formula(row: int, xcell: str) -> str:
    """Linear interpolation of q%% along a capability row at loading X.
    Blank cells (N/A) or loading beyond the last defined column give 0."""
    H = "$B$4:$L$4"
    R = f"$B${row}:$L${row}"
    j = f"MATCH({xcell},{H},1)"
    y1 = f"INDEX({R},1,{j})"
    y2 = f"INDEX({R},1,{j}+1)"
    x1 = f"INDEX({H},1,{j})"
    x2 = f"INDEX({H},1,{j}+1)"
    return (f'=IF({xcell}>=1,IF(ISNUMBER(INDEX({R},1,11)),INDEX({R},1,11),0),'
            f'IF(OR(NOT(ISNUMBER({y1}))),0,'
            f'IF({xcell}={x1},{y1},'
            f'IF(NOT(ISNUMBER({y2})),0,'
            f'{y1}+({y2}-{y1})*({xcell}-{x1})/({x2}-{x1})))))')


pq["A13"] = "Sizing lookup (1.00 Vn row at PF loading):"
pq["A13"].font = BOLD
pq["A14"] = "Loading (= inverter PF)"
pq["B14"] = "=Sizing!B33"
style(pq, "B14", CALC, num="0.000")
pq["A15"] = "q% at 1.00 Vn"
pq["B15"] = interp_formula(7, "$B$14")
style(pq, "B15", CALC, num="0.00")
pq["A16"] = "q (kVAr) at 1.00 Vn"
pq["B16"] = "=B15/100*Sizing!B32"
style(pq, "B16", CALC, num="0.0")

# =============================== COMPLIANCE ===============================
cp = wb.create_sheet("Compliance")
for col, w in zip("ABCDEFGHIJK", (12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12)):
    cp.column_dimensions[col].width = w
section(cp, "A1", "COMPLIANCE VS SELECTED GRID CODE")
cp["A2"] = "Dispatch/inverter"
cp["B2"] = "=Sizing!B29*1000/Sizing!B44"
cp["C2"] = "kW"
style(cp, "B2", CALC, num="0.0")
cp["A3"] = "Dispatch loading"
cp["B3"] = "=B2/Sizing!B32"
cp["C3"] = "pu"
style(cp, "B3", CALC, num="0.000")
cp["A4"] = "Qmax required"
cp["B4"] = "=GridCodes!B15*Sizing!B5"
cp["C4"] = "MVAr"
style(cp, "B4", CALC, num="0.00")

# ---- V-Q at Registered Capacity ----
section(cp, "A6", "V-Q AT REGISTERED CAPACITY (table voltages)")
vq_headers = ["V (pu)", "q%/inv", "Q prod (MVAr)", "Q abs (MVAr)", "Req lag", "Req lead", "Status"]
for j, h in enumerate(vq_headers):
    c = f"{get_column_letter(j+1)}7"
    cp[c] = h
    cp[c].font = BOLD
# symmetric / asymmetric V factors, per direction
FL, FH, ZL, ZH, ASYM = "GridCodes!$H$15", "GridCodes!$I$15", "GridCodes!$K$15", "GridCodes!$L$15", "GridCodes!$J$15"


def vq_lag(v):
    sym = (f"IF(OR({v}<={ZL},{v}>={ZH}),0,IF({v}<{FL},({v}-{ZL})/({FL}-{ZL}),"
           f"IF({v}>{FH},({ZH}-{v})/({ZH}-{FH}),1)))")
    asym = f"IF(OR({v}<{FL}-0.0001,{v}>{FH}+0.0001),0,IF({v}<=1,1,({FH}-{v})/({FH}-1)))"
    return f"IF({ASYM}=1,{asym},{sym})"


def vq_lead(v):
    sym = (f"IF(OR({v}<={ZL},{v}>={ZH}),0,IF({v}<{FL},({v}-{ZL})/({FL}-{ZL}),"
           f"IF({v}>{FH},({ZH}-{v})/({ZH}-{FH}),1)))")
    asym = f"IF(OR({v}<{FL}-0.0001,{v}>{FH}+0.0001),0,IF({v}>=1,1,({v}-{FL})/(1-{FL})))"
    return f"IF({ASYM}=1,{asym},{sym})"


for i in range(6):  # rows follow the InverterPQ table voltages
    r = 8 + i
    pq_row = 5 + i
    cp[f"A{r}"] = f"=InverterPQ!A{pq_row}"
    style(cp, f"A{r}", CALC, num="0.00")
    cp[f"B{r}"] = interp_formula(pq_row, "$B$3").replace("$B$4:$L$4", "InverterPQ!$B$4:$L$4").replace(f"$B${pq_row}:$L${pq_row}", f"InverterPQ!$B${pq_row}:$L${pq_row}")
    style(cp, f"B{r}", CALC, num="0.0")
    cp[f"C{r}"] = f"=Sizing!$B$44*B{r}/100*Sizing!$B$32/1000+Sizing!$B$39-Sizing!$B$19"
    style(cp, f"C{r}", CALC, num="0.00")
    cp[f"D{r}"] = f"=Sizing!$B$44*B{r}/100*Sizing!$B$32/1000+Sizing!$B$19"
    style(cp, f"D{r}", CALC, num="0.00")
    cp[f"E{r}"] = f"=$B$4*({vq_lag(f'A{r}')})"
    style(cp, f"E{r}", CALC, num="0.00")
    cp[f"F{r}"] = f"=$B$4*({vq_lead(f'A{r}')})"
    style(cp, f"F{r}", CALC, num="0.00")
    cp[f"G{r}"] = f'=IF(AND(MAX(0,C{r})>=E{r}-0.001,MAX(0,D{r})>=F{r}-0.001),"PASS","FAIL")'
    style(cp, f"G{r}", CALC)

# requirement polygon vertices for the chart (Q, V), closed — works for both
# the asymmetric G99 hexagon and the symmetric taper hexagon
cp["I7"] = "Req polygon"
cp["I7"].font = BOLD
cp["I8"], cp["J8"] = "Q", "V"
poly = [
    ("=0", f"=IF({ASYM}=1,{FL},{ZL})"),
    ("=$B$4", f"={FL}"),
    ("=$B$4", f"=IF({ASYM}=1,1,{FH})"),
    ("=0", f"=IF({ASYM}=1,{FH},{ZH})"),
    ("=-$B$4", f"={FH}"),
    ("=-$B$4", f"=IF({ASYM}=1,1,{FL})"),
    ("=0", f"=IF({ASYM}=1,{FL},{ZL})"),
]
for i, (qf, vf) in enumerate(poly):
    cp[f"I{9+i}"] = qf
    cp[f"J{9+i}"] = vf
    style(cp, f"I{9+i}", CALC, num="0.00")
    style(cp, f"J{9+i}", CALC, num="0.00")

# ---- P-Q at nominal voltage ----
section(cp, "A20", "P-Q AT NOMINAL VOLTAGE (1.00 pu)")
pq_headers = ["P (pu)", "P (MW)", "disp (kW)", "loading", "q%/inv", "Q prod", "Q abs", "Req lag", "Req lead", "Status"]
for j, h in enumerate(pq_headers):
    c = f"{get_column_letter(j+1)}21"
    cp[c] = h
    cp[c].font = BOLD
PMIN, PFULL, RELIEF = "GridCodes!$D$15", "GridCodes!$E$15", "GridCodes!$F$15"
for i in range(21):
    r = 22 + i
    ppu = i / 20
    cp[f"A{r}"] = ppu
    cp[f"A{r}"].number_format = "0.00"
    cp[f"B{r}"] = f"=A{r}*Sizing!$B$5"
    style(cp, f"B{r}", CALC, num="0.0")
    cp[f"C{r}"] = f"=A{r}*Sizing!$B$29*1000/Sizing!$B$44"
    style(cp, f"C{r}", CALC, num="0.0")
    cp[f"D{r}"] = f"=C{r}/Sizing!$B$32"
    style(cp, f"D{r}", CALC, num="0.000")
    cp[f"E{r}"] = interp_formula(7, f"$D${r}").replace("$B$4:$L$4", "InverterPQ!$B$4:$L$4").replace("$B$7:$L$7", "InverterPQ!$B$7:$L$7")
    style(cp, f"E{r}", CALC, num="0.0")
    cp[f"F{r}"] = f"=Sizing!$B$44*E{r}/100*Sizing!$B$32/1000+Sizing!$B$39-Sizing!$B$19"
    style(cp, f"F{r}", CALC, num="0.00")
    cp[f"G{r}"] = f"=Sizing!$B$44*E{r}/100*Sizing!$B$32/1000+Sizing!$B$19"
    style(cp, f"G{r}", CALC, num="0.00")
    ramp = f"IF({PFULL}<={PMIN},1,MIN(1,(A{r}-{PMIN}/100)/({PFULL}/100-{PMIN}/100)))"
    cp[f"H{r}"] = f"=IF(A{r}<{PMIN}/100-0.0001,0,$B$4*{ramp})"
    style(cp, f"H{r}", CALC, num="0.00")
    relief = (f"IF(A{r}>=0.5,$B$4,$B$4*0.12/0.33+($B$4-$B$4*0.12/0.33)*(A{r}-{PMIN}/100)/(0.5-{PMIN}/100))")
    cp[f"I{r}"] = f"=IF(A{r}<{PMIN}/100-0.0001,0,IF({RELIEF}=1,{relief},$B$4*{ramp}))"
    style(cp, f"I{r}", CALC, num="0.00")
    cp[f"J{r}"] = f'=IF(AND(MAX(0,F{r})>=H{r}-0.001,MAX(0,G{r})>=I{r}-0.001),"PASS","FAIL")'
    style(cp, f"J{r}", CALC)
# chart helper columns: negative lead values
cp["K21"] = "-Req lead"
cp["K21"].font = BOLD
cp["L21"] = "-Q abs"
cp["L21"].font = BOLD
for i in range(21):
    r = 22 + i
    cp[f"K{r}"] = f"=-I{r}"
    cp[f"L{r}"] = f"=-G{r}"
    style(cp, f"K{r}", CALC, num="0.00")
    style(cp, f"L{r}", CALC, num="0.00")
cp["N7"] = "-Q abs (VQ)"
cp["N7"].font = BOLD
for i in range(6):
    r = 8 + i
    cp[f"N{r}"] = f"=-D{r}"
    style(cp, f"N{r}", CALC, num="0.00")

cp["A44"] = "OVERALL VERDICT"
cp["A44"].font = BOLD
cp["B44"] = '=IF(COUNTIF(G8:G13,"FAIL")+COUNTIF(J22:J42,"FAIL")=0,"COMPLIANT","NOT COMPLIANT")'
style(cp, "B44", RESULT, bold=True)

# ---- charts ----
vq_chart = ScatterChart()
vq_chart.title = "V-Q Diagram at CP - Registered Capacity"
vq_chart.x_axis.title = "Q at CP (MVAr)   [lead < 0 < lag]"
vq_chart.y_axis.title = "V (pu)"
vq_chart.height, vq_chart.width = 10, 17


def scat(xref, yref, title):
    return Series(yref, xref, title=title)


vq_chart.series.append(scat(Reference(cp, min_col=9, min_row=9, max_row=15), Reference(cp, min_col=10, min_row=9, max_row=15), "Requirement"))
vq_chart.series.append(scat(Reference(cp, min_col=3, min_row=8, max_row=13), Reference(cp, min_col=1, min_row=8, max_row=13), "Capability (lag)"))
vq_chart.series.append(scat(Reference(cp, min_col=14, min_row=8, max_row=13), Reference(cp, min_col=1, min_row=8, max_row=13), "Capability (lead)"))
cp.add_chart(vq_chart, "L1")

pq_chart = ScatterChart()
pq_chart.title = "P-Q Diagram at CP - 1.00 pu"
pq_chart.x_axis.title = "Q at CP (MVAr)   [lead < 0 < lag]"
pq_chart.y_axis.title = "P (MW)"
pq_chart.height, pq_chart.width = 10, 17
pq_chart.series.append(scat(Reference(cp, min_col=8, min_row=22, max_row=42), Reference(cp, min_col=2, min_row=22, max_row=42), "Req (lag)"))
pq_chart.series.append(scat(Reference(cp, min_col=11, min_row=22, max_row=42), Reference(cp, min_col=2, min_row=22, max_row=42), "Req (lead)"))
pq_chart.series.append(scat(Reference(cp, min_col=6, min_row=22, max_row=42), Reference(cp, min_col=2, min_row=22, max_row=42), "Capability (lag)"))
pq_chart.series.append(scat(Reference(cp, min_col=12, min_row=22, max_row=42), Reference(cp, min_col=2, min_row=22, max_row=42), "Capability (lead)"))
cp.add_chart(pq_chart, "L20")

for ch in (vq_chart, pq_chart):
    for ser in ch.series:
        ser.marker.symbol = "circle"
        ser.marker.size = 4

out = "Reactive_Power_Compensation_Tool.xlsx"
wb.save(out)
print("saved", out)
