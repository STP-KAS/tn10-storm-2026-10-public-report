#!/usr/bin/env python3
"""Prints the markdown tables used in README.md from the CSVs in data/ (so the README numbers are reproducible)."""
import csv, os
D = os.path.dirname(os.path.abspath(__file__))
sc = list(csv.DictReader(open(f"{D}/mainnet_scenarios.csv")))
def f(x, nd=0): return f"{float(x):,.{nd}f}"
for shape in ("P2W", "signed"):
    for rate in ("peak 1 min", "peak 10 min", "sustained: best 60 min", "sustained: whole-test"):
        R = [r for r in sc if r["shape"].startswith(shape) and r["rate"].startswith(rate)]
        r0 = R[0]
        print(f"\n**{r0['rate']}: {f(r0['tps'],1)} tx/s, {r0['shape']} {r0['mass_g']} g** — mainnet capacity for this shape {f(r0['mainnet_capacity_tps'])} tx/s; uses {r0['pct_of_mainnet_mass_capacity']}% of block mass; fits: {'yes' if r0['fits_mainnet']=='True' else '**NO**'}\n")
        print("| Duration | Txs | KAS @ normal 100 sompi/g | KAS @ priority 150 sompi/g | USD normal | USD priority | EUR normal | EUR priority |")
        print("|---|---:|---:|---:|---:|---:|---:|---:|")
        for r in R:
            h = float(r["duration_h"]); d = f"{int(h*60)} min" if h < 1 else f"{h:g} h"
            print(f"| {d} | {f(r['txs'])} | {f(r['kas_normal_100'])} | {f(r['kas_priority_150'])} | {f(r['usd_normal'])} | {f(r['usd_priority'])} | {f(r['eur_normal'])} | {f(r['eur_priority'])} |")
