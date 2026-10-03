#!/usr/bin/env python3
"""Public API stall/503/freeze windows vs the load at the time, and how long recovery took.
Inputs : data/api_events.csv-style raw samplers (stress-tests/data/api-health-min.jsonl every 120 s,
         api-mined-watch.jsonl every 300 s), data/box_5min.csv (box included tx/s),
         n0 kaspad log 'Processed' lines (network-wide upper bound, all senders, double-counting).
Output : data/api_windows_vs_load.csv
Recovery = first health sample after the window with lag < 120 s and HTTP 200 (and, for the coinbase view,
newest coinbase lag < 120 s). "minutes from window end" is bounded by the 120-s / 300-s sampling interval.
"""
import json, csv, os, sys, re, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/artifacts/stress-tests/data"
LOG = sys.argv[2] if len(sys.argv) > 2 else "/workspace/kaspa-logs-tn10-n0/rusty-kaspa.log"
OUT = os.path.dirname(os.path.abspath(__file__))
TZ = dt.timezone(dt.timedelta(hours=2))
U = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp()
T = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
C = lambda t: dt.datetime.fromtimestamp(t, TZ).strftime("%a %H:%M")
def load(f):
    R = []
    for l in open(f"{SRC}/{f}"):
        try: j = json.loads(l)
        except Exception: continue
        if "ts" in j and ("http" in j or "error" in j): j["t"] = T(j["ts"]); R.append(j)
    return R
H = load("api-health-min.jsonl"); M = load("api-mined-watch.jsonl")
box = []
for r in csv.DictReader(open(f"{OUT}/box_5min.csv")):
    t = dt.datetime.strptime("2026 " + r["bin_start_cest"][4:], "%Y %d %b %H:%M:%S").replace(tzinfo=TZ).timestamp()
    box.append((t, float(r["box_included_tps"])))
rx = re.compile(r"^(\S+ \S+)\+02:00 \[INFO \] Processed (\d+) blocks and \d+ headers in the last ([\d.]+)s \((\d+) transactions;")
net = []
if os.path.exists(LOG):
    for line in open(LOG, errors="ignore"):
        if not line.startswith("2026-10-0") or "Processed" not in line: continue
        m = rx.match(line)
        if m: net.append((dt.datetime.fromisoformat(m.group(1)).replace(tzinfo=TZ).timestamp(), int(m.group(2)), float(m.group(3)), int(m.group(4))))
def box_avg(a, b):
    v = [x for t, x in box if a <= t < b]; return round(sum(v) / len(v)) if v else ""
def box_max(a, b):
    v = [(x, t) for t, x in box if a <= t < b]; return (round(max(v)[0]), C(max(v)[1])) if v else ("", "")
def net_avg(a, b):
    P = [p for p in net if a <= p[0] < b]; s = sum(p[2] for p in P)
    return round(sum(p[3] - p[1] for p in P) / s) if s else ""
def first_ok_after(t0, kind):
    if kind == "health":
        for j in H:
            if j["t"] > t0 and j.get("http") == 200 and (j.get("acceptedTxBlockTimeDiff") or 999) < 120: return j["t"]
    else:
        for j in M:
            if j["t"] > t0 and j.get("http") == 200 and (j.get("newest_tx_lag_s") or 9e9) < 120: return j["t"]
# Windows (CEST): picked from data/api_events.csv; boundaries = first/last flagged sample
W = [
 ("L1 health: indexer lag >120 s (stall) with intermittent 503", "health", "2026-10-01T22:29:30", "2026-10-01T23:31:30", "lagging, not frozen: lag rose and fell between 137 and 704 s"),
 ("L1 health: continuous 503 (isSynced false)", "health", "2026-10-01T23:03:30", "2026-10-01T23:29:30", "subset of the window above"),
 ("L1 coinbase view: mined_stall", "mined", "2026-10-01T22:56:13", "2026-10-01T23:31:12", "newest qzffl5 coinbase 306-651 s old"),
 ("L1 health: stall + 503 again", "health", "2026-10-01T23:53:30", "2026-10-02T00:09:30", "health sampler then stopped 00:09-01:00; runners paused 00:10-01:10"),
 ("L1 coinbase view: mined_stall again", "mined", "2026-10-02T00:01:13", "2026-10-02T00:06:13", "mined-watch sampler then stopped 00:06-08:45"),
 ("L1 health: 503 with slow responses (18 s), then stall", "health", "2026-10-02T01:22:31", "2026-10-02T01:30:31", "during the 30x-fee burst 01:10-01:27 that gave the L1 1-min peak (01:24:46)"),
 ("L2 health: stall (preceded by 6 timeouts 09:39-09:51)", "health", "2026-10-02T09:55:39", "2026-10-02T09:57:39", "right after the L2 1-min/10-s peaks (09:52-09:54)"),
 ("L3 health: two 503 + intermittent stall", "health", "2026-10-02T12:25:49", "2026-10-02T12:47:49", "lag 22-170 s, rose and fell; not at the L3 peak (11:55)"),
 ("L4 health: full indexer freeze, 503 every sample 22:09-23:27", "health", "2026-10-02T22:01:49", "2026-10-02T23:27:49", "lag grew ~120 s per 120-s sample: no progress at all"),
 ("L4 coinbase view frozen", "mined", "2026-10-02T22:03:55", "2026-10-02T23:23:55", "same newest coinbase id 22:23-23:18; mined_stall flag could not fire (share counter 0)"),
]
rows = []
for name, kind, a, b, note in W:
    ta, tb = U(a), U(b); rec = first_ok_after(tb, kind)
    pk, pkt = box_max(ta - 300, tb + 300)
    rows.append(dict(window=name, start_cest=C(ta), end_cest=C(tb), minutes=round((tb - ta) / 60),
        box_tps_avg_in_window=box_avg(ta - 300, tb), box_tps_avg_hour_before=box_avg(ta - 3600, ta),
        box_best_5min_bin_in_window=pk, box_best_5min_bin_at=pkt, n0_processed_tps_avg_in_window=net_avg(ta, tb),
        recovered_at_cest=C(rec) if rec else "", recovery_min_after_last_bad_sample=round((rec - tb) / 60) if rec else "", note=note))
with open(f"{OUT}/api_windows_vs_load.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
for r in rows: print(r)
