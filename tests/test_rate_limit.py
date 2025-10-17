import os
import time
import json
import random
import string
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8001")
USERS = int(os.getenv("LT_USERS", "100"))
TOTAL_REQUESTS = int(os.getenv("LT_REQUESTS", "10000"))
CONCURRENCY = int(os.getenv("LT_CONCURRENCY", "100"))
CREATE_CONCURRENCY = int(os.getenv("LT_CREATE_CONCURRENCY", "10"))
TARGET_ENDPOINT = os.getenv("LT_ENDPOINT", "/usage")  # authenticated endpoint


def random_name(prefix: str) -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{suffix}"


def create_user(session: requests.Session, max_retries: int = 5, base_timeout: float = 10.0) -> str:
    username = random_name("user")
    email = f"{username}@example.com"
    for attempt in range(max_retries):
        try:
            resp = session.post(
                f"{API_BASE}/users/",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"username": username, "email": email}),
                timeout=base_timeout + attempt * 5.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["api_key"]
        except Exception:
            # Exponential backoff with jitter
            sleep_s = min(2 ** attempt, 8) + random.random()
            time.sleep(sleep_s)
    # final attempt raises
    resp = session.post(
        f"{API_BASE}/users/",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"username": username, "email": email}),
        timeout=base_timeout + max_retries * 5.0,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["api_key"]


def fire_request(session: requests.Session, api_key: str):
    t0 = time.perf_counter()
    try:
        resp = session.get(
            f"{API_BASE}{TARGET_ENDPOINT}",
            headers={"X-API-Key": api_key},
            timeout=10,
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return resp.status_code, latency_ms
    except Exception:
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return 599, latency_ms


def main():
    print(f"Starting load test: users={USERS}, total_requests={TOTAL_REQUESTS}, concurrency={CONCURRENCY}")
    s = requests.Session()

    # 1) Create users and collect API keys (limited concurrency and retries)
    api_keys: list[str] = []
    create_errors = 0
    create_lock = threading.Lock()

    def create_task(_: int):
        nonlocal create_errors
        try:
            key = create_user(s)
            with create_lock:
                api_keys.append(key)
        except Exception:
            with create_lock:
                create_errors += 1

    with ThreadPoolExecutor(max_workers=CREATE_CONCURRENCY) as ex:
        futures = [ex.submit(create_task, i) for i in range(USERS)]
        for _ in as_completed(futures):
            pass

    if len(api_keys) < USERS:
        print(f"Warning: created {len(api_keys)} of {USERS} users (errors={create_errors})")
    else:
        print(f"Created {len(api_keys)} users")

    # 2) Fire requests
    results = []
    start = time.perf_counter()
    lock = threading.Lock()

    def task(i: int):
        key = api_keys[i % USERS]
        code, latency = fire_request(s, key)
        with lock:
            results.append((code, latency))

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = [ex.submit(task, i) for i in range(TOTAL_REQUESTS)]
        for _ in as_completed(futures):
            pass

    duration_s = time.perf_counter() - start

    # 3) Stats
    codes = {}
    latencies = []
    for code, latency in results:
        codes[code] = codes.get(code, 0) + 1
        latencies.append(latency)

    latencies.sort()
    def pct(p):
        if not latencies:
            return 0.0
        k = int(round((p / 100.0) * (len(latencies) - 1)))
        return latencies[k]

    total = len(results)
    success = sum(count for c, count in codes.items() if 200 <= c < 300)
    rps = total / duration_s if duration_s > 0 else 0

    print("\n=== Load Test Results ===")
    print(f"Total: {total} in {duration_s:.2f}s | RPS: {rps:.1f}")
    print("Status codes:", dict(sorted(codes.items())))
    summary = {
        "total": total,
        "duration_s": round(duration_s, 3),
        "rps": round(rps, 1),
        "codes": dict(sorted(codes.items())),
        "latency_ms": {}
    }
    if latencies:
        summary["latency_ms"] = {
            "p50": round(pct(50), 1),
            "p90": round(pct(90), 1),
            "p95": round(pct(95), 1),
            "p99": round(pct(99), 1),
            "max": round(latencies[-1], 1),
            "mean": round(statistics.mean(latencies), 1),
            "stdev": round(statistics.pstdev(latencies), 1)
        }
        print(f"Latency ms: p50={summary['latency_ms']['p50']:.1f} p90={summary['latency_ms']['p90']:.1f} p95={summary['latency_ms']['p95']:.1f} p99={summary['latency_ms']['p99']:.1f} max={summary['latency_ms']['max']:.1f}")
        print(f"Mean={summary['latency_ms']['mean']:.1f} stdev={summary['latency_ms']['stdev']:.1f}")

    # Write JSON summary for later inspection
    try:
        with open("tests/load_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print("Summary written to tests/load_results.json")
    except Exception:
        pass


if __name__ == "__main__":
    main()


