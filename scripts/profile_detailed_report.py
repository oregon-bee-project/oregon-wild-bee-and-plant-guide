#!/usr/bin/env python3
"""
Measure wall time and heap growth for the detailed-report backend pipeline.

Hotspots to validate with real data (same relative paths as uvicorn from src/backend):

1. **parse_viz_to_dataframe** — loading the full `.viz` tables dominates startup RSS.
2. **search_by_location.filter_df** — region filtering over all observations for the bbox/region.
3. **detailed_report.everySpeciesList** — one full pass per request; builds Counters and a
   sorted species list; pagination only shrinks the JSON, not this scan.
4. **create_pdf.generate_detailed_pdf** (optional `--pdf`) — ReportLab build; per-species
   `KeepTogether` retains layout structures proportional to species count.

**Large-export follow-ups (design):**

- Warn or gate when `numRows` or `beeListTotal` exceeds a configurable threshold; offer async
  “prepare download” for PDF/ZIP instead of holding the full buffer in one request.
- Prefer streaming responses and `Content-Length` where possible; align with the frontend’s
  `showSaveFilePicker` streaming path for prompt 3 in `src/frontend/src/Pages/DataDisplay.jsx`.
- Consider short-TTL cache of `filtered_df` keyed by region hash if `filter_df` dominates.

Usage (repo root; requires data files at paths used by the backend):

  python scripts/profile_detailed_report.py --lat 44.05 --long -123.08 --region-type county
  python scripts/profile_detailed_report.py --lat 44.05 --long -123.08 --region-type county --pdf
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import tracemalloc


def _rss_mb() -> float | None:
    try:
        import psutil

        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile detailed-report backend stages.")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--long", type=float, required=True)
    parser.add_argument("--region-type", type=str, default="county")
    parser.add_argument("--pdf", action="store_true", help="Also time generate_detailed_pdf")
    parser.add_argument("--species-limit", type=int, default=None, help="Pass to everySpeciesList")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    backend_dir = os.path.join(repo_root, "src", "backend")
    if not os.path.isdir(backend_dir):
        print("Expected src/backend directory at:", backend_dir, file=sys.stderr)
        return 1

    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)

    tracemalloc.start()
    rss0 = _rss_mb()

    t0 = time.perf_counter()
    import parse_viz as pv
    import search_by_location as sl
    import detailed_report as dr

    t_import = time.perf_counter()
    print(f"stage=import_modules wall_s={t_import - t0:.3f} rss_mb={_rss_mb()}")

    subset_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz"
    taxa_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz"
    if not os.path.isfile(os.path.join(backend_dir, subset_path)):
        print(
            "Missing data file:",
            os.path.normpath(os.path.join(backend_dir, subset_path)),
            file=sys.stderr,
        )
        print("Place OBA .viz inputs there or run this script from an environment with data.", file=sys.stderr)
        return 1

    t_df0 = time.perf_counter()
    full_df = pv.parse_viz_to_dataframe(subset_path)
    inat_key = pv.parse_viz_to_dataframe(taxa_path)
    t_df1 = time.perf_counter()
    print(
        f"stage=load_dataframes wall_s={t_df1 - t_df0:.3f} "
        f"rows={len(full_df.index)} rss_mb={_rss_mb()}"
    )

    response_json = {
        "response": [],
        "region_type": args.region_type,
        "region_name": "",
        "lat": args.lat,
        "long": args.long,
        "error": False,
        "err_msg": "",
    }

    snap_a = tracemalloc.take_snapshot()
    t_f0 = time.perf_counter()
    filtered_df = sl.filter_df(response_json, full_df)
    t_f1 = time.perf_counter()
    snap_b = tracemalloc.take_snapshot()
    if response_json.get("error"):
        print("filter_df error:", response_json.get("err_msg"), file=sys.stderr)
        return 1
    print(
        f"stage=filter_df wall_s={t_f1 - t_f0:.3f} "
        f"filtered_rows={len(filtered_df.index)} rss_mb={_rss_mb()}"
    )
    _print_tracemalloc_diff(snap_a, snap_b, limit=8)

    limit = args.species_limit
    snap_c = tracemalloc.take_snapshot()
    t_e0 = time.perf_counter()
    dr.everySpeciesList(
        response_json,
        inat_key,
        filtered_df,
        bee_list_offset=0,
        bee_list_limit=limit,
    )
    t_e1 = time.perf_counter()
    snap_d = tracemalloc.take_snapshot()
    stats = response_json.get("response") or {}
    print(
        f"stage=everySpeciesList wall_s={t_e1 - t_e0:.3f} "
        f"beeList_len={len(stats.get('beeList', []))} "
        f"beeListTotal={stats.get('beeListTotal')} rss_mb={_rss_mb()}"
    )
    _print_tracemalloc_diff(snap_c, snap_d, limit=8)

    if args.pdf:
        from create_pdf import generate_detailed_pdf

        if not stats:
            print("No stats for PDF", file=sys.stderr)
            return 1
        dr.everySpeciesList(response_json, inat_key, filtered_df, bee_list_limit=None)
        stats_full = response_json.get("response") or {}

        snap_e = tracemalloc.take_snapshot()
        t_p0 = time.perf_counter()
        buf = generate_detailed_pdf(
            stats_full,
            title="Detailed Bee and Plant Report",
            location=response_json.get("region_name") or "Oregon",
            filtered_df=filtered_df,
        )
        t_p1 = time.perf_counter()
        snap_f = tracemalloc.take_snapshot()
        try:
            nbytes = buf.getbuffer().nbytes
        except Exception:
            nbytes = -1
        print(
            f"stage=generate_detailed_pdf wall_s={t_p1 - t_p0:.3f} "
            f"buffer_bytes={nbytes} rss_mb={_rss_mb()}"
        )
        _print_tracemalloc_diff(snap_e, snap_f, limit=8)

    rss1 = _rss_mb()
    print(f"stage=total wall_s={time.perf_counter() - t0:.3f} rss_mb_start={rss0} rss_mb_end={rss1}")
    return 0


def _print_tracemalloc_diff(snap_before, snap_after, limit: int = 8) -> None:
    lines = []
    for stat in snap_after.compare_to(snap_before, "lineno")[:limit]:
        lines.append(str(stat))
    if lines:
        print("  tracemalloc top growth:")
        for line in lines:
            print("   ", line)


if __name__ == "__main__":
    raise SystemExit(main())
