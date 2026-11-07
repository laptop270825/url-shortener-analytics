import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

BASE = "http://127.0.0.1:8000"
TOTAL = 2000
WORKERS = 20


def benchmark(client, path):
    # def one(_):
    #     t = time.perf_counter()
    #     r = client.get(path, follow_redirects=False)
    #     return time.perf_counter() - t, r.status_code
    def one(_):
        t = time.perf_counter()
        try:
            r = client.get(path, follow_redirects=False)
            status = r.status_code
        except httpx.HTTPError:
            status = 599
        return time.perf_counter() - t, status

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(one, range(TOTAL)))
    elapsed = time.perf_counter() - start

    latencies = sorted(t for t, _ in results)
    errors = sum(1 for _, s in results if s >= 400)
    print(path)
    print(f"  requests/sec : {TOTAL / elapsed:.0f}")
    print(f"  median       : {statistics.median(latencies) * 1000:.1f} ms")
    print(f"  p95          : {latencies[int(0.95 * len(latencies))] * 1000:.1f} ms")
    print(f"  errors       : {errors}")
    return errors


def main():
    client = httpx.Client(base_url=BASE, timeout=30)
    code = client.post("/shorten", json={"url": "https://www.google.com"}).json()["short_code"]

    errors = benchmark(client, f"/{code}")
    counted = client.get(f"/stats/{code}").json()["click_count"]
    expected = TOTAL - errors
    print(f"  click_count  : {counted} (expected {expected})")
    print("  consistent   : " + ("YES" if counted == expected else "NO - clicks were lost"))

    benchmark(client, f"/stats/{code}")
    benchmark(client, "/api/analytics")


if __name__ == "__main__":
    main()