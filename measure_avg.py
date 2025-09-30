import time, statistics
from augment import generate_single  # adjust import to your file
import tempfile, os


def measure_avg(n=200):
    tmpdir = tempfile.mkdtemp()
    times = []
    for i in range(n):
        t0 = time.perf_counter()
        generate_single(i, tmpdir)
        times.append(time.perf_counter() - t0)
    avg = statistics.mean(times)
    p90 = statistics.quantiles(times, n=10)[8]
    print(f"Avg task: {avg * 1000:.2f} ms, p90: {p90 * 1000:.2f} ms")
    return avg, p90


if __name__ == "__main__":
    avg, p90 = measure_avg()
    desired_chunk_time = 0.15  # 150 ms
    chunk_size = max(1, int(desired_chunk_time / avg))
    print(f"Suggested chunk_size ≈ {chunk_size} (round to 16/32/64).")
