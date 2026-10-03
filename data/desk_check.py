#!/usr/bin/env python3
"""Desk-side tables for the public report. Standard library only.

Reads three local inputs and writes CSVs next to this script. Raw logs are not
copied: they hold transaction ids. This script is not part of run_all.sh.

  python3 desk_check.py SENDER_JSONL STORM2_LOG_DIR P2W_LOG_DIR

Counters, as implemented by the desk runners on 3 Oct 2026:

- sender.jsonl batch.accepted is incremented when a submit resolves as success.
  The submit path treats an already/duplicate/exists error as success. The field
  is a submit result. It is not a virtual-chain inclusion.
- chainPerSec is every accepted id returned by getVirtualChainFromBlock between
  two sink samples, divided by the seconds between those samples. All senders
  on that node. Null when the call fails.
- build-storm2 status.accepted_tx_s sums each worker's submit-ok rate.
  accepted_total and spent_tkas on status lines are not a running total: worker
  files reset. final.accepted_total is the harvested counter at exit.
- P2W scale_minute included/s is this process's txids delivered by the local
  node's virtual-chain-changed events over the previous 60 seconds.
"""
import csv, json, os, re, sys, datetime as dt
from pathlib import Path

TZ = dt.timezone(dt.timedelta(hours=2))
CUT = dt.datetime.fromisoformat("2026-10-02T07:40:33.393+00:00")
HERE = Path(__file__).resolve().parent
HEX = re.compile(r"[0-9a-fA-F]{16,}")


def cest(ts):
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)


def hour_key(label):
    return dt.datetime.strptime(label, "%a %d %b %H:00").replace(year=2026)


def write_csv(name, rows, fields):
    path = HERE / name
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    text = path.read_text(encoding="utf-8")
    if HEX.search(text):
        raise SystemExit(f"refusing to write {name}: long hex token")
    if "kaspatest:" in text or ":\\" in text:
        raise SystemExit(f"refusing to write {name}: secret-like token")
    return path


def sender_tables(path):
    hours = {}
    pre = [0, 0, 0, 0]
    post = [0, 0, 0, 0]
    first = last = None
    chain_n = chain_null = 0
    chain_max = None
    chain_max_t = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                j = json.loads(line)
            except Exception:
                continue
            if j.get("ev") != "batch":
                continue
            t = dt.datetime.fromisoformat(j["t"].replace("Z", "+00:00"))
            if first is None:
                first = j["t"]
            last = j["t"]
            triple = (int(j["submitted"]), int(j["accepted"]), int(j["rejected"]))
            label = cest(j["t"]).strftime("%a %d %b %H:00")
            slot = hours.setdefault(label, [0, 0, 0, 0])
            bucket = pre if t <= CUT else post
            for i, v in enumerate(triple):
                slot[i] += v
                bucket[i] += v
            slot[3] += 1
            bucket[3] += 1
            cp = j.get("chainPerSec")
            if cp is None:
                chain_null += 1
            else:
                chain_n += 1
                cp = int(cp)
                if chain_max is None or cp > chain_max:
                    chain_max = cp
                    chain_max_t = j["t"]
    rows = []
    for label in sorted(hours, key=hour_key):
        sub, ack, rej, n = hours[label]
        rows.append({
            "hour_cest": label,
            "batches": n,
            "submitted": sub,
            "accepted_field": ack,
            "rejected": rej,
        })
    rows.append({
        "hour_cest": "TOTAL through 2026-10-02T07:40:33.393Z",
        "batches": pre[3], "submitted": pre[0], "accepted_field": pre[1], "rejected": pre[2],
    })
    rows.append({
        "hour_cest": "TOTAL after that timestamp",
        "batches": post[3], "submitted": post[0], "accepted_field": post[1], "rejected": post[2],
    })
    rows.append({
        "hour_cest": "TOTAL whole file",
        "batches": pre[3] + post[3],
        "submitted": pre[0] + post[0],
        "accepted_field": pre[1] + post[1],
        "rejected": pre[2] + post[2],
    })
    write_csv("desk_batch_hours.csv", rows,
              ["hour_cest", "batches", "submitted", "accepted_field", "rejected"])
    return {
        "first": first, "last": last, "pre": pre, "post": post,
        "chain_n": chain_n, "chain_null": chain_null,
        "chain_max": chain_max, "chain_max_t": chain_max_t,
    }


def storm2_tables(log_dir):
    peaks = []
    finals = []
    long_rows = []
    for path in sorted(Path(log_dir).glob("*.log")):
        best = None
        statuses = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("{"):
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            ev = j.get("ev")
            if ev == "status":
                rate = int(j.get("accepted_tx_s") or 0)
                statuses.append(j)
                if best is None or rate > int(best.get("accepted_tx_s") or 0):
                    best = j
            elif ev == "final":
                finals.append({
                    "log_file": path.name,
                    "t_utc": j.get("t"),
                    "minutes": j.get("minutes"),
                    "workers_last": j.get("workers_last"),
                    "accepted_total": j.get("accepted_total"),
                    "rejects_total": j.get("rejects_total"),
                    "stale_total": j.get("stale_total"),
                    "avg_tx_s": j.get("avg_tx_s"),
                    "spent_tkas": j.get("spent_tkas"),
                    "stopped": j.get("stopped"),
                })
        if best is not None and int(best.get("accepted_tx_s") or 0) >= 5000:
            peaks.append({
                "log_file": path.name,
                "t_utc": best.get("t"),
                "accepted_tx_s": best.get("accepted_tx_s"),
                "mempool": best.get("mempool"),
                "workers": best.get("workers"),
                "alive": best.get("alive"),
            })
        if path.name == "x10-20261003-010247.log" and statuses:
            drops = 0
            prev = None
            last_nz = None
            for j in statuses:
                total = j.get("accepted_total")
                if prev is not None and total is not None and total < prev:
                    drops += 1
                prev = total
                if int(j.get("accepted_tx_s") or 0) > 0:
                    last_nz = j
            last = statuses[-1]
            long_rows.append({
                "log_file": path.name,
                "which": "last_accepted_tx_s_above_zero",
                "t_utc": last_nz.get("t") if last_nz else "",
                "accepted_tx_s": last_nz.get("accepted_tx_s") if last_nz else "",
                "mempool": last_nz.get("mempool") if last_nz else "",
                "accepted_total_drops": drops,
            })
            long_rows.append({
                "log_file": path.name,
                "which": "last_status_line",
                "t_utc": last.get("t"),
                "accepted_tx_s": last.get("accepted_tx_s"),
                "mempool": last.get("mempool"),
                "accepted_total_drops": drops,
            })
    peaks.sort(key=lambda r: -int(r["accepted_tx_s"]))
    write_csv("desk_submit_ok_peaks.csv", peaks,
              ["log_file", "t_utc", "accepted_tx_s", "mempool", "workers", "alive"])
    write_csv("desk_final_lines.csv", finals,
              ["log_file", "t_utc", "minutes", "workers_last", "accepted_total",
               "rejects_total", "stale_total", "avg_tx_s", "spent_tkas", "stopped"])
    write_csv("desk_long_run.csv", long_rows,
              ["log_file", "which", "t_utc", "accepted_tx_s", "mempool", "accepted_total_drops"])
    return peaks, finals, long_rows


def heart_max(path):
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"(\d+)\s+sub=(\d+)\s+vcc=(\d+)", line.strip())
        if m:
            rows.append((int(m.group(1)), int(m.group(3))))
    best = None
    j = 0
    for i, (t0, v0) in enumerate(rows):
        while j < len(rows) and rows[j][0] - t0 < 60000:
            j += 1
        if j >= len(rows):
            break
        t1, v1 = rows[j]
        dv = v1 - v0
        if dv < 0:
            continue
        window = t1 - t0
        rate = dv / (window / 1000)
        if best is None or rate > best[0]:
            best = (rate, t0, window)
    if best is None:
        return None
    rate, t0, window = best
    stamp = dt.datetime.fromtimestamp(t0 / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # trim microseconds to milliseconds to match the log style loosely
    stamp = stamp[:-4] + "Z"
    return {"rate": round(rate, 1), "t_utc": stamp, "window_ms": window}


def p2w_tables(log_dir):
    status = Path(log_dir) / "status.log"
    best = None
    best_l4 = None
    l4_start = dt.datetime.fromisoformat("2026-10-02T19:52:07+00:00")
    l4_end = dt.datetime.fromisoformat("2026-10-02T23:06:29+00:00")
    for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
        if "scale_minute" not in line:
            continue
        tm = re.match(r"(\S+)", line)
        inc = re.search(r"included/s=([0-9.]+)", line)
        if not (tm and inc):
            continue
        t = dt.datetime.fromisoformat(tm.group(1).replace("Z", "+00:00"))
        rate = float(inc.group(1))
        row = (rate, tm.group(1), line)
        if best is None or rate > best[0]:
            best = row
        if l4_start <= t <= l4_end and (best_l4 is None or rate > best_l4[0]):
            best_l4 = row

    def fields(row, meter):
        line = row[2]
        def grab(pat):
            m = re.search(pat, line)
            return m.group(1) if m else ""
        return {
            "meter": meter,
            "t_utc": row[1],
            "per_second": row[0],
            "lanes": grab(r"lanes=(\d+/\d+)"),
            "feerate": grab(r"feerate=([0-9.]+)"),
            "orphans": grab(r"orphans=(\d+)"),
            "source_file": "status.log",
            "note": "printed scale_minute included/s",
        }

    rows = [fields(best, "highest_printed_scale_minute")]
    if best_l4:
        rows.append(fields(best_l4, "highest_printed_scale_minute_during_L4"))
    heart = Path(log_dir) / "scale-heart.log"
    h = heart_max(heart)
    if h:
        rows.append({
            "meter": "computed_60s_vcc_rise",
            "t_utc": h["t_utc"],
            "per_second": h["rate"],
            "lanes": "",
            "feerate": "",
            "orphans": "",
            "source_file": "scale-heart.log",
            "note": f"cumulative vcc rise over {h['window_ms']} ms; computed, not a printed rate",
        })
    for tag in ("a", "b"):
        hp = Path(log_dir) / f"scale-heart-{tag}.log"
        if not hp.exists():
            continue
        h = heart_max(hp)
        if not h:
            continue
        rows.append({
            "meter": f"computed_60s_vcc_rise_tag_{tag}",
            "t_utc": h["t_utc"],
            "per_second": h["rate"],
            "lanes": "",
            "feerate": "",
            "orphans": "",
            "source_file": hp.name,
            "note": "overlaps the other tagged heart file; not added to it",
        })
    write_csv("desk_p2w_peaks.csv", rows,
              ["meter", "t_utc", "per_second", "lanes", "feerate", "orphans", "source_file", "note"])
    return rows


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: desk_check.py SENDER_JSONL STORM2_LOG_DIR P2W_LOG_DIR")
    sender = sender_tables(sys.argv[1])
    peaks, finals, long_rows = storm2_tables(sys.argv[2])
    p2w = p2w_tables(sys.argv[3])
    print("SENDER", json.dumps(sender))
    print("PEAKS", len(peaks), "top", peaks[0] if peaks else None)
    print("FINALS", len(finals))
    print("LONG", long_rows)
    print("P2W", p2w)


if __name__ == "__main__":
    main()
