#!/usr/bin/env python3
"""n0 mempool size, n0 fee estimate and mempool evictions per window (context for third-party txs stuck pending).
Inputs : stress-tests/data/host.jsonl ('mempool' = n0 mempool tx count, every 15-30 s),
         stress-tests/data/feerate.jsonl (n0 GetFeeEstimate normal/priority, every 30 s),
         n0 kaspad log 'Mempool stats: N transactions were evicted from the mempool in favor of incoming higher feerate transactions'.
Caveat : only COUNTS are logged. Mempool composition (which txs, script types, pending times) was NOT sampled, so this
         cannot show whether third-party / covenant txs were among the pending or evicted ones.
Outputs: data/mempool_windows.csv, data/mempool_evictions_10min.csv
"""
import json, csv, os, sys, re, statistics as st, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/artifacts/stress-tests/data"
LOG = sys.argv[2] if len(sys.argv) > 2 else "/workspace/kaspa-logs-tn10-n0/rusty-kaspa.log"
OUT = os.path.dirname(os.path.abspath(__file__)); TZ = dt.timezone(dt.timedelta(hours=2))
U = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp()
H, F = [], []
for l in open(f"{SRC}/host.jsonl"):
    try: j = json.loads(l)
    except Exception: continue
    if j.get("type") == "host" and "mempool" in j:
        H.append((dt.datetime.fromisoformat(j["ts"].replace("Z", "+00:00")).timestamp(), j["mempool"]))
for l in open(f"{SRC}/feerate.jsonl"):
    try: j = json.loads(l)
    except Exception: continue
    if "normal" in j:
        t = j["t"]; F.append((dt.datetime.fromisoformat(t[:22] + ":" + t[22:]).timestamp(), j["normal"], j["priority"]))
EV = []
rx = re.compile(r"^(\S+ \S+)\+02:00 \[INFO \] Mempool stats: (\d+) transactions were evicted")
for line in open(LOG, errors="ignore"):
    if "evicted from the mempool" not in line: continue
    m = rx.match(line)
    if m: EV.append((dt.datetime.fromisoformat(m.group(1)).replace(tzinfo=TZ).timestamp(), int(m.group(2))))
W = [("pre-storm baseline", "2026-10-01T18:41", "2026-10-01T20:35"), ("L1 box miners on", "2026-10-01T20:35", "2026-10-02T01:32"),
     ("L1 peak incl. 30x fee burst 01:10-01:30", "2026-10-02T01:10", "2026-10-02T01:30"), ("L1 night, box miners off", "2026-10-02T01:32", "2026-10-02T07:53"),
     ("L2", "2026-10-02T09:07", "2026-10-02T10:15"), ("L3 loaded", "2026-10-02T11:52", "2026-10-02T13:04"),
     ("L4 loaded", "2026-10-02T21:57", "2026-10-02T23:38"), ("L4 peak 23:10-23:25", "2026-10-02T23:10", "2026-10-02T23:25"),
     ("after the storm Sat 01:06-17:00", "2026-10-03T01:06", "2026-10-03T17:00")]
rows = []
for n, a, b in W:
    m = sorted(v for t, v in H if U(a) <= t < U(b)); f = [(x, y) for t, x, y in F if U(a) <= t < U(b)]
    ev = sum(v for t, v in EV if U(a) <= t < U(b))
    rows.append(dict(window_cest=n, mempool_samples=len(m), mempool_median=round(st.median(m)) if m else "",
        mempool_p95=m[int(.95 * len(m)) - 1] if m else "", mempool_max=max(m) if m else "",
        fee_est_normal_median=round(st.median([x for x, _ in f]), 1) if f else "", fee_est_normal_max=round(max(x for x, _ in f), 1) if f else "",
        fee_est_priority_max=round(max(y for _, y in f), 1) if f else "", evicted_for_higher_feerate=ev))
with open(f"{OUT}/mempool_windows.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
B = {}
for t, v in EV:
    k = dt.datetime.fromtimestamp(int(t) // 600 * 600, TZ).strftime("%a %d %b %H:%M"); B[k] = B.get(k, 0) + v
with open(f"{OUT}/mempool_evictions_10min.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["bin_start_cest", "evicted_for_higher_feerate"]); [w.writerow([k, v]) for k, v in B.items()]
for r in rows: print(r)
print("evictions total", sum(B.values()), B)
