#!/usr/bin/env python3
"""Public API (api-tn10.kaspa.org) behaviour during the storm legs.
Inputs : stress-tests/data/api-health-min.jsonl (GET /info/health every 120 s; 300 s before 1 Oct 18:27 UTC),
         stress-tests/data/api-mined-watch.jsonl (every 300 s: newest coinbase of the qzffl5 mining address on
         /addresses/<qzffl5>/full-transactions-page vs blocks n0 saw us mine in the same window).
Outputs: data/api_legs.csv (per leg), data/api_events.csv (every non-200 / timeout / stall sample), data/api_gaps.csv
stall_suspected (set by the sampler): acceptedTxBlockTimeDiff > 120 s while the API's kaspad backends were synced,
i.e. the API's database/indexer is behind the chain, not the node.
"""
import json, csv, os, sys, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/artifacts/stress-tests/data"
OUT = os.path.dirname(os.path.abspath(__file__))
TZ = dt.timezone(dt.timedelta(hours=2)); U = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp()
T = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
C = lambda t: dt.datetime.fromtimestamp(t, TZ).strftime("%a %d %b %H:%M")
def load(f):
    R = []
    for l in open(f"{SRC}/{f}"):
        try: j = json.loads(l)
        except Exception: continue
        if j.get("type") in ("health", "mined"): j["t"] = T(j["ts"]); R.append(j)
    return R
H = load("api-health-min.jsonl"); M = load("api-mined-watch.jsonl")
LEGS = [("baseline Thu 18:41-20:35", "2026-10-01T18:41:30", "2026-10-01T20:35:18"),
        ("L1", "2026-10-01T20:35:18", "2026-10-02T07:52:54"), ("L2", "2026-10-02T09:07:39", "2026-10-02T10:15:00"),
        ("L3", "2026-10-02T11:49:49", "2026-10-02T16:50:47"), ("L4", "2026-10-02T21:52:07", "2026-10-03T01:06:29"),
        ("after Sat 01:06-17:55", "2026-10-03T01:06:29", "2026-10-03T17:56:00")]
rows = []
for n, a, b in LEGS:
    a, b = U(a), U(b); h = [x for x in H if a <= x["t"] < b]; m = [x for x in M if a <= x["t"] < b]
    lag = [x["acceptedTxBlockTimeDiff"] for x in h if isinstance(x.get("acceptedTxBlockTimeDiff"), (int, float))]
    st = [x for x in h if x.get("stall_suspected")]
    ml = [x["newest_coinbase_lag_s"] for x in m if isinstance(x.get("newest_coinbase_lag_s"), (int, float))]
    rows.append(dict(window_cest=n, health_samples=len(h), health_503=sum(1 for x in h if x.get("http") == 503),
        health_502=sum(1 for x in h if x.get("http") == 502), health_timeouts=sum(1 for x in h if "error" in x),
        stall_suspected_samples=len(st), first_stall=C(st[0]["t"]) if st else "", last_stall=C(st[-1]["t"]) if st else "",
        max_indexer_lag_s=round(max(lag), 1) if lag else "", max_indexer_lag_at=C(h[[x.get("acceptedTxBlockTimeDiff") for x in h].index(max(lag))]["t"]) if lag else "",
        mined_samples=len(m), mined_timeouts=sum(1 for x in m if "error" in x), mined_stall_true=sum(1 for x in m if x.get("mined_stall")),
        max_newest_coinbase_lag_s=round(max(ml), 1) if ml else "", max_coinbase_lag_at=C(m[[x.get("newest_coinbase_lag_s") for x in m].index(max(ml))]["t"]) if ml else ""))
with open(f"{OUT}/api_legs.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
with open(f"{OUT}/api_events.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["time_cest", "probe", "http", "error", "indexer_lag_s_or_coinbase_lag_s", "db_isSynced", "stall_or_mined_stall", "health_ok_within_3min"])
    for x in sorted(H + M, key=lambda x: x["t"]):
        bad = x.get("http") not in (200, None) or "error" in x or x.get("stall_suspected") or x.get("mined_stall")
        if not bad: continue
        if x["type"] == "health":
            w.writerow([C(x["t"]), "/info/health", x.get("http", ""), x.get("error", "")[:40], x.get("acceptedTxBlockTimeDiff", ""), x.get("db_isSynced", ""), x.get("stall_suspected", ""), ""])
        else:
            near = [h for h in H if abs(h["t"] - x["t"]) <= 180]
            ok = any(h.get("http") == 200 and not h.get("stall_suspected") for h in near)
            w.writerow([C(x["t"]), "qzffl5 full-transactions-page", x.get("http", ""), x.get("error", "")[:40], x.get("newest_coinbase_lag_s", ""), "", x.get("mined_stall", ""), ok])
with open(f"{OUT}/api_gaps.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["probe", "gap_start_cest", "gap_end_cest", "minutes"])
    for name, R, iv in (("health", H, 120), ("mined-watch", M, 300)):
        for p, q in zip(R, R[1:]):
            if q["t"] - p["t"] > 3 * iv: w.writerow([name, C(p["t"]), C(q["t"]), round((q["t"] - p["t"]) / 60)])
for r in rows: print(r)
print(open(f"{OUT}/api_gaps.csv").read())
