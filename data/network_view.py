#!/usr/bin/env python3
"""Network-wide view (all TN10 traffic n0 saw, not only the box runners).
Inputs : n0 kaspad log 'Processed N blocks ... (M transactions; ... mass: s/c/t)' lines (10-s windows)
         api-tn10 /transactions/count/<day> hourly 'regular' counts (data/sources/count-*.json, fetched 3 Oct 2026 15:55 UTC)
         data/box_5min.csv (box-only, from runners_tps.py) for the hourly box comparison
Outputs: data/network_legs.csv, data/hourly_network_vs_box.csv
Caveat : kaspad 'transactions' counts every tx in every block body processed, so a tx that sits in two
         parallel blocks is counted twice, and each block's coinbase is counted. It is an UPPER bound for
         unique throughput. The indexer 'regular' count is unique accepted non-coinbase txs per UTC hour.
"""
import re, sys, os, json, csv, glob, datetime as dt
OUT = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(OUT)
LOG = sys.argv[1] if len(sys.argv) > 1 else "/workspace/kaspa-logs-tn10-n0/rusty-kaspa.log"
TZ = dt.timezone(dt.timedelta(hours=2))
U = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp()
LEGS = [("L1", U("2026-10-01T20:35:18"), U("2026-10-02T07:52:54")), ("L2", U("2026-10-02T09:07:39"), U("2026-10-02T10:15:00")),
        ("L3", U("2026-10-02T11:49:49"), U("2026-10-02T16:50:47")), ("L4", U("2026-10-02T21:52:07"), U("2026-10-03T01:06:29"))]
rx = re.compile(r"^(\S+ \S+)\+02:00 \[INFO \] Processed (\d+) blocks and \d+ headers in the last ([\d.]+)s \((\d+) transactions;.*?mass: ([\d.]+)s/([\d.]+)c/([\d.]+)t")
pts = []
for line in open(LOG, errors="ignore"):
    if not line.startswith("2026-10-0") or "Processed" not in line: continue
    m = rx.match(line)
    if not m: continue
    t = dt.datetime.fromisoformat(m.group(1)).replace(tzinfo=TZ).timestamp()
    b, sec, tx = int(m.group(2)), float(m.group(3)), int(m.group(4))
    pts.append((t, b, sec, tx, float(m.group(5)), float(m.group(6)), float(m.group(7))))
cest = lambda t: dt.datetime.fromtimestamp(t, TZ).strftime("%a %d %b %H:%M:%S")
rows = []
for L, a, z in LEGS:
    P = [p for p in pts if a <= p[0] <= z]
    rate = [((p[3] - p[1]) / p[2]) for p in P]   # minus one coinbase per block
    def best(n):
        bv, bt = 0, 0
        for i in range(len(P) - n + 1):
            v = sum(rate[i:i+n]) / n
            if v > bv: bv, bt = v, P[i][0] - P[i][2]
        return round(bv), cest(bt)
    loaded = [p for p in P if (p[3]-p[1])/p[2] > 1000]
    c_full = [p[5] for p in loaded if p[1] > 0]
    r = dict(leg=L, log_lines=len(P), blocks_per_s=round(sum(p[1] for p in P)/sum(p[2] for p in P), 2))
    for n, lab in ((1, "10s"), (6, "60s"), (30, "300s"), (60, "600s"), (360, "3600s")):
        v, t = best(n); r[f"processed_peak_{lab}_tps"] = v; r[f"processed_peak_{lab}_start_cest"] = t
    r["mean_compute_mass_per_block_when_loaded"] = round(sum(c_full)/len(c_full)) if c_full else ""
    r["pct_of_500k_compute_when_loaded"] = round(100*sum(c_full)/len(c_full)/500000, 1) if c_full else ""
    r["max_10s_mean_compute_mass"] = round(max(p[5] for p in P)) if P else ""
    r["max_10s_mean_storage_mass"] = round(max(p[4] for p in P)) if P else ""
    r["max_10s_mean_transient_mass"] = round(max(p[6] for p in P)) if P else ""
    rows.append(r)
with open(f"{OUT}/network_legs.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
print(json.dumps(rows, indent=1))
# hourly: indexer regular vs box included (box_5min.csv is CEST, convert)
idx = {}
for f in sorted(glob.glob(f"{OUT}/sources/count-*.json")) or sorted(glob.glob(f"{ROOT}/raw/count-*.json")):
    for h in json.load(open(f)): idx[h["timestamp"]//1000] = (h["regular"], h["coinbase"])
box = {}
for r in csv.DictReader(open(f"{OUT}/box_5min.csv")):
    t = dt.datetime.strptime("2026 " + r["bin_start_cest"][4:], "%Y %d %b %H:%M:%S").replace(tzinfo=TZ).timestamp()
    h = int(t)//3600*3600; box[h] = box.get(h, 0) + float(r["box_included_tps"])*300
with open(f"{OUT}/hourly_network_vs_box.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["hour_start_cest", "indexer_regular_txs", "indexer_regular_tps", "box_included_txs", "box_tps", "other_senders_tps_(indexer-box)"])
    for h in sorted(idx):
        if not (U("2026-10-01T18:00:00") <= h <= U("2026-10-03T02:00:00")): continue
        reg = idx[h][0]; b = round(box.get(h, 0))
        w.writerow([cest(h)[:-3], reg, round(reg/3600, 1), b, round(b/3600, 1), round((reg-b)/3600, 1)])
