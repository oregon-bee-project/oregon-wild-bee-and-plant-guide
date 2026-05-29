"""
Basic concurrent stress checks for heavy backend routes.

Usage:
  python stress_test.py
"""

import threading
import time
from collections import Counter

import requests

BASE_URL = "https://oregon-wild-bee-and-plant-guide.onrender.com"
COORDS = {"lat": 44.56, "long": -123.26, "region_type": "county"}
HEAVY_GET = f"{BASE_URL}/api/detailed-report/"
HEAVY_EXPORT = f"{BASE_URL}/api/export-detailed-pdf/"
THREADS = 12
TIMEOUT_SECONDS = 120

results = Counter()
lock = threading.Lock()


def hit_detailed_report(i: int) -> None:
    try:
        response = requests.get(
            HEAVY_GET,
            params={
                **COORDS,
                "species_offset": 0,
                "species_limit": 100,
            },
            timeout=TIMEOUT_SECONDS,
        )
        with lock:
            results[f"detailed:{response.status_code}"] += 1
        print(f"[detailed] worker={i} status={response.status_code}")
    except Exception as exc:
        with lock:
            results["detailed:error"] += 1
        print(f"[detailed] worker={i} error={exc}")


def hit_export(i: int) -> None:
    try:
        response = requests.post(
            HEAVY_EXPORT,
            json={
                "selectedCoords": {"lat": COORDS["lat"], "lng": COORDS["long"]},
                "region_type": COORDS["region_type"],
            },
            timeout=TIMEOUT_SECONDS,
        )
        with lock:
            results[f"export:{response.status_code}"] += 1
        print(f"[export]   worker={i} status={response.status_code}")
    except Exception as exc:
        with lock:
            results["export:error"] += 1
        print(f"[export]   worker={i} error={exc}")


def run_group(label: str, target) -> None:
    print(f"\n=== Running {label} with {THREADS} parallel requests ===")
    threads = []
    started = time.time()
    for i in range(THREADS):
        thread = threading.Thread(target=target, args=(i,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    elapsed = time.time() - started
    print(f"=== {label} complete in {elapsed:.2f}s ===")


if __name__ == "__main__":
    total_start = time.time()
    run_group("detailed-report", hit_detailed_report)
    run_group("export-detailed-pdf", hit_export)
    print("\nStatus summary:")
    for key in sorted(results.keys()):
        print(f"  {key}: {results[key]}")
    print(f"\nFinished in {time.time() - total_start:.2f} seconds")
