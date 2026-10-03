#!/usr/bin/env python3
"""Grok Build desk sender (stp's desk PC -> public TN10 wRPC nodes), from desk/sender.jsonl in the private
analysis repo. Each 'batch' line is one batch: submitted / accepted (= node accepted submitTransaction,
NOT seen in a block) / rejected. The copy in the repo ends Thu 1 Oct 23:23 CEST.
The full desk log was summed later in desk_batch_hours.csv. This script still sums whatever file it is given.
Its TOTAL label stays the Thu 23:23 copy.
Output: data/desk_sender_summary.csv (per hour, CEST)
"""
import json, csv, os, sys, datetime as dt, collections
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/repos/tn10-storm-2026-10-analysis/desk/sender.jsonl"
OUT = os.path.dirname(os.path.abspath(__file__)); TZ = dt.timezone(dt.timedelta(hours=2))
H = collections.defaultdict(lambda: [0, 0, 0])
for l in open(SRC):
    try: j = json.loads(l)
    except Exception: continue
    if j.get("ev") != "batch": continue
    h = dt.datetime.fromisoformat(j["t"].replace("Z", "+00:00")).astimezone(TZ).strftime("%a %d %b %H:00")
    H[h][0] += j["submitted"]; H[h][1] += j["accepted"]; H[h][2] += j["rejected"]
with open(f"{OUT}/desk_sender_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["hour_cest", "submitted", "node_acked", "rejected"])
    for h, v in H.items(): w.writerow([h] + v)
    w.writerow(["TOTAL (repo copy, to Thu 23:23 CEST)"] + [sum(v[i] for v in H.values()) for i in range(3)])
print(open(f"{OUT}/desk_sender_summary.csv").read())
