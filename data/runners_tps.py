#!/usr/bin/env python3
"""Box-only throughput, fees and mass per leg, from the storm runner logs.
Input : stress-tests/data/runner1-4.out (SMX) and p2w1-8.out (P2W): 'rep' lines every 10 s
        (cumulative submitted / accepted-on-virtual-chain / fee_tkas) and 'final' lines.
Output: data/runner_segments.csv, data/legs_box.csv (incl. peaks), data/box_5min.csv, data/fee_recapture_estimate.csv
Method: each runner segment's cumulative 'accepted' is linearly interpolated onto a 1-s grid
        (0 at first rep - 10 s), the per-second increments of all segments are summed, and
        sliding windows of 10/60/300/600/3600 s are taken. Times are reported in CEST (UTC+2).
"""
import json, glob, csv, sys, os, datetime as dt, statistics as st
SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/artifacts/stress-tests/data"
OUT = os.path.dirname(os.path.abspath(__file__))
UTC = dt.timezone.utc
def P(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
def E(s): return int(P(s).timestamp())
def cest(ts): return (dt.datetime.fromtimestamp(ts, UTC) + dt.timedelta(hours=2)).strftime("%a %d %b %H:%M:%S")
def U(s): return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone(dt.timedelta(hours=2))).timestamp())
# Legs (CEST). start = launch, load_end = when runners stopped sending for good (pause/STOP), end = STOP/kill
LEGS = [
 ("L1", "Thu 1 Oct 20:35 -> Fri 2 Oct 07:53", U("2026-10-01T20:35:18"), U("2026-10-02T07:52:54")),
 ("L2", "Fri 2 Oct 09:07 -> 10:15 (reboot)",   U("2026-10-02T09:07:39"), U("2026-10-02T10:15:00")),
 ("L3", "Fri 2 Oct 11:49 -> 16:51 (STOP)",     U("2026-10-02T11:49:49"), U("2026-10-02T16:50:47")),
 ("L4", "Fri 2 Oct 21:52 -> Sat 3 Oct 01:06 (STOP)", U("2026-10-02T21:52:07"), U("2026-10-03T01:06:29")),
]
def leg_of(ts):
    for L in LEGS:
        if L[2] - 60 <= ts <= L[3] + 600: return L[0]
    return None
segs = []
for f in sorted(glob.glob(f"{SRC}/runner[0-9].out")) + sorted(glob.glob(f"{SRC}/p2w[0-9].out")):
    cur = None
    def close():
        if cur and cur["pts"]: segs.append(cur)
    for line in open(f):
        if not line.startswith("{"): continue
        try: j = json.loads(line)
        except Exception: continue
        ev = j.get("ev")
        if ev not in ("rep", "final"): continue
        t = E(j["t"])
        if ev == "rep":
            sub, acc = j.get("submitted", 0), j.get("accepted", 0)
            if cur is None or cur["final"] or sub < cur["sub"]:
                close()
                cur = dict(file=os.path.basename(f), tag=j["tag"], kind=("SMX" if j["tag"].startswith("SMX") else "P2W"),
                           pts=[], sub=0, acc=0, fee=0.0, final=False, mass_tot=None, n_mass=None,
                           hop_avg=j.get("mass_hop_avg"), fund_avg=j.get("mass_fund_avg"), hops=0, funded=0, feer=[])
            cur["pts"].append((t, acc)); cur.update(rej=j.get("rejected", 0), sub=sub, acc=acc, fee=j.get("fee_tkas", 0.0),
                hops=j.get("hops", 0), funded=j.get("funded", 0))
            cur["feer"].append((t, j.get("feerate"), sub, j.get("fee_tkas", 0.0)))
            if j.get("mass_hop_avg"): cur["hop_avg"] = j["mass_hop_avg"]
        else:
            if cur is None or cur["final"]:
                close(); cur = dict(file=os.path.basename(f), tag=j["tag"], kind=("SMX" if j["tag"].startswith("SMX") else "P2W"),
                                    pts=[], sub=0, acc=0, fee=0.0, final=False, mass_tot=None, n_mass=None, hop_avg=None, fund_avg=None, hops=0, funded=0, feer=[])
            fa = j["accepted_seen_vcc"]
            cur["pts"].append((t, max(fa, cur["acc"])))
            cur.update(rej=j.get("rejected", 0), sub=j["submitted"], acc=fa, fee=j["fee_tkas"], final=True, hops=j.get("hops", 0), funded=j.get("funded", 0))
            if "massH" in j:
                cur["mass_tot"] = j["massH"] + j["massF"]; cur["n_mass"] = j["nH"] + j["nF"]
    close()
# SMX mass estimate from fee deltas: d(fee)/(d(submitted)*feerate) over rep pairs with constant feerate
def smx_mass(s):
    ms = []
    fr = s["feer"]
    for (t0, r0, s0, f0), (t1, r1, s1, f1) in zip(fr, fr[1:]):
        if r0 and r0 == r1 and s1 - s0 > 500:
            ms.append((f1 - f0) * 1e8 / ((s1 - s0) * r1))
    return st.median(ms) if ms else None
rows = []
for s in segs:
    s["start"] = s["pts"][0][0] - 10; s["end"] = s["pts"][-1][0]; s["leg"] = leg_of(s["start"] + 10)
    if s["kind"] == "P2W":
        if s["mass_tot"] is None and s["hop_avg"]:
            s["mass_tot"] = s["hop_avg"] * s["hops"] + (s["fund_avg"] or 1701) * s["funded"]; s["n_mass"] = s["hops"] + s["funded"]; s["mass_src"] = "rep avg"
        else: s["mass_src"] = "final massH+massF"
    else:
        m = smx_mass(s); s["mass_tot"] = m * s["sub"] if m else None; s["n_mass"] = s["sub"]; s["mass_src"] = "fee/(submitted*feerate) median"
    s["avg_mass"] = s["mass_tot"] / s["n_mass"] if s["mass_tot"] and s["n_mass"] else None
    rows.append(s)
with open(f"{OUT}/runner_segments.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["leg","file","tag","kind","start_cest","end_cest","submitted","included","rejected","fee_tkas","avg_mass_g","mass_source","has_final_line"])
    for s in rows: w.writerow([s["leg"], s["file"], s["tag"], s["kind"], cest(s["start"]), cest(s["end"]), s["sub"], s["acc"], s.get("rej", 0), round(s["fee"], 6), round(s["avg_mass"], 1) if s["avg_mass"] else "", s["mass_src"], s["final"]])
# 1-s grid
lo = min(s["start"] for s in rows); hi = max(s["end"] for s in rows) + 1
N = hi - lo; inc = [0.0] * N
for s in rows:
    pts = [(s["start"], 0)] + s["pts"]
    for (t0, a0), (t1, a1) in zip(pts, pts[1:]):
        if t1 <= t0 or a1 <= a0: continue
        r = (a1 - a0) / (t1 - t0)
        for x in range(t0, t1): inc[x - lo] += r
pref = [0.0]
for v in inc: pref.append(pref[-1] + v)
# fee grid (cumulative fee_tkas per segment, interpolated the same way)
finc = [0.0] * N
for s in rows:
    fpts = [(s["start"], 0.0)] + [(t, f) for (t, r, sb, f) in s["feer"]]
    if s["final"]: fpts.append((s["end"], s["fee"]))
    for (t0, f0), (t1, f1) in zip(fpts, fpts[1:]):
        if t1 <= t0 or f1 <= f0: continue
        r = (f1 - f0) / (t1 - t0)
        for x in range(t0, t1): finc[x - lo] += r
fpref = [0.0]
for v in finc: fpref.append(fpref[-1] + v)
def fees(a, b): a = max(a, lo); b = min(b, hi); return fpref[b - lo] - fpref[a - lo] if b > a else 0.0
def best(a, b, W):
    a = max(a, lo); b = min(b, hi); bestv, bt = 0, a
    for x in range(a, b - W + 1):
        v = pref[x - lo + W] - pref[x - lo]
        if v > bestv: bestv, bt = v, x
    return bestv / W, bt
def total(a, b): a = max(a, lo); b = min(b, hi); return pref[b - lo] - pref[a - lo]
legrows, peakrows = [], []
for L, name, a, b in LEGS:
    S = [s for s in rows if s["leg"] == L]
    inc_n = sum(s["acc"] for s in S); sub_n = sum(s["sub"] for s in S); fee = sum(s["fee"] for s in S)
    mass = sum(s["avg_mass"] * s["acc"] for s in S if s["avg_mass"])
    first = min(s["start"] for s in S); last = max(s["end"] for s in S)
    # loaded time = seconds with box inclusion >= 100 tx/s
    loaded = sum(1 for x in range(first, last) if inc[x - lo] >= 100)
    bins = [ (pref[min(x+300,hi)-lo]-pref[x-lo])/300 for x in range(first - (first%300), last, 300) if x >= lo]
    act = [v for v in bins if v >= 100]
    pk = {W: best(first, last + 1, W) for W in (10, 60, 300, 600, 3600)}
    legrows.append(dict(leg=L, window=name, first_send_cest=cest(first), last_report_cest=cest(last), wall_h=round((last-first)/3600, 2),
        loaded_h_ge100tps=round(loaded/3600, 2), segments=len(S), submitted=sub_n, included=inc_n, rejected=sum(s.get("rej", 0) for s in S),
        fee_tkas=round(fee, 2), smx_included=sum(s["acc"] for s in S if s["kind"]=="SMX"), p2w_included=sum(s["acc"] for s in S if s["kind"]=="P2W"),
        avg_mass_g=round(mass/inc_n, 1), avg_fee_per_tx_tkas=round(fee/inc_n, 7), avg_feerate_sompi_per_g=round(fee*1e8/mass, 1),
        avg_tps_loaded=round(inc_n/loaded, 1) if loaded else 0, median_5min_active_tps=round(st.median(act), 1) if act else 0,
        **{f"peak_{W}s_tps": round(pk[W][0], 1) for W in (10, 60, 300, 600, 3600)},
        **{f"peak_{W}s_start_cest": cest(pk[W][1]) for W in (10, 60, 300, 600, 3600)}))
cols = list(legrows[0].keys())
allr = dict(leg="ALL", window="all four legs")
for k in ("segments","submitted","included","rejected","fee_tkas","smx_included","p2w_included"): allr[k] = round(sum(r[k] for r in legrows), 2)
allr["wall_h"] = round(sum(r["wall_h"] for r in legrows), 2); allr["loaded_h_ge100tps"] = round(sum(r["loaded_h_ge100tps"] for r in legrows), 2)
m_all = sum(r["avg_mass_g"]*r["included"] for r in legrows)
allr["avg_mass_g"] = round(m_all/allr["included"], 1); allr["avg_fee_per_tx_tkas"] = round(allr["fee_tkas"]/allr["included"], 7)
allr["avg_feerate_sompi_per_g"] = round(allr["fee_tkas"]*1e8/m_all, 1)
allr["avg_tps_loaded"] = round(allr["included"]/(allr["loaded_h_ge100tps"]*3600), 1)
for W in (10, 60, 300, 600, 3600):
    i = max(range(4), key=lambda k: legrows[k][f"peak_{W}s_tps"]); allr[f"peak_{W}s_tps"] = legrows[i][f"peak_{W}s_tps"]; allr[f"peak_{W}s_start_cest"] = legrows[i][f"peak_{W}s_start_cest"]
legrows.append(allr)
with open(f"{OUT}/legs_box.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); [w.writerow(r) for r in legrows]
with open(f"{OUT}/box_5min.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["bin_start_cest", "box_included_tps"])
    for x in range(lo - lo % 300, hi, 300):
        if x < lo: continue
        w.writerow([cest(x), round((pref[min(x+300,hi)-lo]-pref[x-lo])/300, 1)])
# fees per mining-share window (share = box+desk % of blocks, from block_share_legs.csv / block_share_sampler2.csv)
SHW = [("L1 SMX 20:35-21:42", "2026-10-01T20:35:18", "2026-10-01T21:42:37", 57.2, "host.jsonl share"),
       ("L1 P2W box miners on 21:42-01:32", "2026-10-01T21:42:37", "2026-10-02T01:32:17", 60.3, "host.jsonl share"),
       ("L1 box miners off 01:32-07:53", "2026-10-02T01:32:17", "2026-10-02T08:00:00", 0.6, "host.jsonl share"),
       ("L2 09:07-10:15", "2026-10-02T09:07:00", "2026-10-02T10:20:00", 62.8, "host.jsonl share"),
       ("L3 11:49-16:51", "2026-10-02T11:49:00", "2026-10-02T16:55:00", 58.1, "host.jsonl share"),
       ("L4 21:52-01:06", "2026-10-02T21:52:00", "2026-10-03T01:10:00", 52.6, "share-sampler (all blocks via n0)")]
with open(f"{OUT}/fee_recapture_estimate.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["window_cest", "box_included", "fees_tkas", "stp_block_share_pct", "share_source", "est_fees_back_to_stp_tkas", "est_net_fee_tkas"])
    tf = tb = ti = 0
    for n, a, b, sh, src in SHW:
        f = fees(U(a), U(b)); i = total(U(a), U(b)); back = f * sh / 100; tf += f; tb += back; ti += i
        w.writerow([n, round(i), round(f, 2), sh, src, round(back, 2), round(f - back, 2)])
    w.writerow(["ALL", round(ti), round(tf, 2), round(100*tb/tf, 1), "fee-weighted", round(tb, 2), round(tf - tb, 2)])
print("fee recapture written; total fees", round(tf,2), "back", round(tb,2), round(100*tb/tf,1), "%")
# 10-s-bucket (non-interpolated, rep-delta) peak for comparison with the earlier analysis
print(json.dumps(legrows, indent=1))
