#!/usr/bin/env python3
"""Cross-check of mining share with TN10 ops' independent share sampler (every 5 min):
share.csv columns: unix time, n0 virtualDaaScore, cumulative 'Block submitted successfully' lines of the box
miners, cumulative blocks submitted through n0 by any miner (box + desk tunnel; -1 if unknown).
share = growth of the block counter / growth of DAA score (DAA score ~ number of TN10 blocks).
This is the only share source for leg 4 (the host sampler's share counter read 0 after n0's restart).
Output: data/block_share_sampler2.csv
"""
import csv, os, sys, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/artifacts/kaspa-tn10/share.csv"
OUT = os.path.dirname(os.path.abspath(__file__))
TZ = dt.timezone(dt.timedelta(hours=2)); U = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp()
R = [tuple(int(x) for x in l.strip().split(",")) for l in open(SRC) if l.strip()]
def grown(seq):
    g = 0; prev = None
    for v in seq:
        if v < 0: continue
        if prev is not None: g += (v - prev) if v >= prev else v
        prev = v
    return g
W = [("L1 whole", "2026-10-01T20:35:18", "2026-10-02T07:52:54"), ("L1 box miners on 20:57-01:32", "2026-10-01T20:57:46", "2026-10-02T01:32:17"),
     ("L2", "2026-10-02T09:07:39", "2026-10-02T10:15:00"), ("L3 loaded", "2026-10-02T11:52:00", "2026-10-02T13:04:00"),
     ("L3 whole", "2026-10-02T11:49:49", "2026-10-02T16:50:47"), ("L4 whole", "2026-10-02T21:52:07", "2026-10-03T01:06:29"),
     ("L4 loaded", "2026-10-02T21:57:00", "2026-10-02T23:38:00")]
out = []
for n, a, b in W:
    X = [r for r in R if U(a) <= r[0] <= U(b)]
    if len(X) < 2: out.append(dict(window_cest=n, samples=len(X))); continue
    dd = X[-1][1] - X[0][1]; box = grown([r[2] for r in X]); allv = grown([r[3] for r in X if len(r) > 3])
    out.append(dict(window_cest=n, samples=len(X), daa_growth=dd, box_blocks=box, box_pct=round(100*box/dd, 1),
                    all_via_n0_blocks=allv, all_via_n0_pct=round(100*allv/dd, 1) if all(len(r) > 3 and r[3] >= 0 for r in X) else "n/a"))
with open(f"{OUT}/block_share_sampler2.csv", "w", newline="") as fh:
    keys = ["window_cest", "samples", "daa_growth", "box_blocks", "box_pct", "all_via_n0_blocks", "all_via_n0_pct"]
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in out]
for r in out: print(r)
