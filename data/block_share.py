#!/usr/bin/env python3
"""Who mined the blocks n0 saw, per leg (box / desk / rest of TN10).
Input : stress-tests/data/host.jsonl 'share' (per 15-30 s sample: blocks added on n0 by payout + user agent:
        box = qzffl5 payout with the box miners' 'stp grok bot' UA, desk = qzffl5 payout with any other UA,
        network = any other payout). Samples with share.blocks == 0 while blocks were flowing mean the share
        feature was off in that sampler run (start line "share": false) and are reported as 'not measured'.
Output: data/block_share_legs.csv
"""
import json, csv, os, sys, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/artifacts/stress-tests/data/host.jsonl"
OUT = os.path.dirname(os.path.abspath(__file__))
TZ = dt.timezone(dt.timedelta(hours=2)); U = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp()
W = [("pre-storm baseline", "2026-10-01T18:41:30", "2026-10-01T20:35:18"),
     ("L1 SMX 20:35-21:42", "2026-10-01T20:35:18", "2026-10-01T21:42:37"),
     ("L1 P2W, box miners on 21:42-01:32", "2026-10-01T21:42:37", "2026-10-02T01:32:17"),
     ("L1 box miners off 01:32-07:53", "2026-10-02T01:32:17", "2026-10-02T07:52:54"),
     ("L1 whole 20:35-07:53", "2026-10-01T20:35:18", "2026-10-02T07:52:54"),
     ("L2 09:07-10:15", "2026-10-02T09:07:39", "2026-10-02T10:15:00"),
     ("L3 11:49-16:51", "2026-10-02T11:49:49", "2026-10-02T16:50:47"),
     ("L3 loaded 11:52-13:04", "2026-10-02T11:52:00", "2026-10-02T13:04:00"),
     ("L4 21:52-01:06", "2026-10-02T21:52:07", "2026-10-03T01:06:29"),
     ("L4 loaded 21:57-23:38", "2026-10-02T21:57:00", "2026-10-03T23:38:00".replace("03T23","02T23"))]
S = []; share_on = True
for l in open(SRC):
    try: j = json.loads(l)
    except Exception: continue
    if j.get("type") == "start": share_on = bool(j.get("share")); continue
    if j.get("type") != "host": continue
    t = dt.datetime.fromisoformat(j["ts"].replace("Z", "+00:00")).timestamp()
    sh = j.get("share") or {}; bps = (j.get("rate") or {}).get("blocks_submitted_per_s")
    S.append((t, share_on, sh.get("blocks", 0), sh.get("box", 0), sh.get("desk", 0), sh.get("network", 0), bps))
rows = []
for name, a, b in W:
    a, b = U(a), U(b); X = [s for s in S if a <= s[0] < b]
    on = [s for s in X if s[1]]; blk = sum(s[2] for s in on)
    box = sum(s[3] for s in on); desk = sum(s[4] for s in on); net = sum(s[5] for s in on)
    rows.append(dict(window_cest=name, samples=len(X), samples_with_share_on=len(on), blocks_counted=blk,
        box_pct=round(100*box/blk, 1) if blk else "not measured", desk_pct=round(100*desk/blk, 1) if blk else "not measured",
        stp_total_pct=round(100*(box+desk)/blk, 1) if blk else "not measured", rest_of_network_pct=round(100*net/blk, 1) if blk else "not measured"))
with open(f"{OUT}/block_share_legs.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
for r in rows: print(r)
