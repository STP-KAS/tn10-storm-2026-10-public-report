#!/usr/bin/env python3
"""Plain mainnet storm cost: same tx shape (measured mass) and measured TN10 rates, priced at
(a) the mainnet normal feerate = minimum relay fee 100 sompi/gram and (b) priority = 1.5 x normal = 150 sompi/gram.
No fee recapture from mining, no fee-market / bidding-war model (deliberately left out, see README).
Capacity check: mainnet 10 blocks/s x 500,000 normalized block mass = 5,000,000 g/s.
Outputs: data/mainnet_scenarios.csv (every rate x shape x duration), data/mainnet_actual_test.csv
"""
import csv, os
OUT = os.path.dirname(os.path.abspath(__file__))
SOMPI = 1e8
BPS, BLOCK_MASS = 10, 500_000                      # rusty-kaspa MAINNET_PARAMS (see README sources)
CAP_G_PER_S = BPS * BLOCK_MASS
NORMAL, PRIORITY = 100, 150                         # sompi/gram; 100 = min relay fee = live api.kaspa.org normal estimate
PRICE_USD, PRICE_EUR = 0.04243, 0.03778             # Kraken KASUSD / KASEUR last trade, 2026-10-03 15:57:59/15:58:05 UTC
SHAPES = {"P2W hop (measured avg incl. funding txs)": 644.8, "signed P2PK 1-in-1-out (SMX, measured)": 1751.9}
RATES = {"peak 1 min (L1, Fri 01:24:46)": 4252.8, "peak 10 min (L1, Fri 01:16:11)": 3717.3,
         "sustained: best 60 min (L4, Fri 21:57)": 2517.6, "sustained: whole-test loaded average": 1417.9}
DUR_H = [0.5, 1, 2, 3, 4, 10, 12, 24]
rows = []
for shape, mass in SHAPES.items():
    cap = CAP_G_PER_S / mass
    for rname, tps in RATES.items():
        fits = tps <= cap
        for h in DUR_H:
            n = tps * 3600 * h
            kn = n * mass * NORMAL / SOMPI; kp = n * mass * PRIORITY / SOMPI
            rows.append(dict(shape=shape, mass_g=mass, rate=rname, tps=tps, mainnet_capacity_tps=round(cap), fits_mainnet=fits,
                             pct_of_mainnet_mass_capacity=round(100 * tps * mass / CAP_G_PER_S, 1), duration_h=h, txs=round(n),
                             kas_normal_100=round(kn, 2), kas_priority_150=round(kp, 2),
                             usd_normal=round(kn * PRICE_USD, 2), usd_priority=round(kp * PRICE_USD, 2),
                             eur_normal=round(kn * PRICE_EUR, 2), eur_priority=round(kp * PRICE_EUR, 2)))
with open(f"{OUT}/mainnet_scenarios.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
# the actual test, repriced (box-only included txs per leg from legs_box.csv)
legs = list(csv.DictReader(open(f"{OUT}/legs_box.csv")))
out = []
for L in legs:
    n = int(float(L["included"])); m = float(L["avg_mass_g"]) * n
    kn, kp, ka = m * NORMAL / SOMPI, m * PRIORITY / SOMPI, float(L["fee_tkas"])
    out.append(dict(leg=L["leg"], included_txs=n, avg_mass_g=L["avg_mass_g"], total_mass_g=round(m),
                    kas_at_100=round(kn, 2), kas_at_150=round(kp, 2), kas_at_feerates_used=round(ka, 2), avg_feerate_used=L["avg_feerate_sompi_per_g"],
                    usd_at_100=round(kn * PRICE_USD, 2), usd_at_150=round(kp * PRICE_USD, 2), usd_at_feerates_used=round(ka * PRICE_USD, 2)))
with open(f"{OUT}/mainnet_actual_test.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); [w.writerow(r) for r in out]
for r in out: print(r)
