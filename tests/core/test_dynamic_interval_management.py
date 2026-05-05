import data_streaming_accelerators.core.dynamic_interval_management as dim

import os

def write_to_summary(sizes, results_v2, results_v3):
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write("### 🚀 Streaming Benchmark Results\n")
            f.write("| N | Batch (Two-Pointer) | Tree (AVL) | Speedup |\n")
            f.write("|---|---|---|---|\n")
            for i, n in enumerate(sizes):
                speedup = results_v2[i] / results_v3[i]
                f.write(f"| {n} | {results_v2[i]:.4f}s | {results_v3[i]:.4f}s | **{speedup:.1f}x** |\n")

import json
import sys

def test_benchmark_static():
    """Simple test runner to verify correctness in static case."""
    test_cases = [
        ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
        ([[1, 4], [4, 5]], [[1, 5]]),
        ([[1, 10], [2, 3], [4, 5], [6, 7], [8, 9]], [[1, 10]]),
    ]
    
    variants = [
        dim.DynamicIntervalManagementV1(), 
        dim.DynamicIntervalManagementV2(), 
        dim.DynamicIntervalManagementV3(), 
    ]

    for i, sol in enumerate(variants, 1):
        # print(f"--- Testing Variant {i} ---")
        for intervals, expected in test_cases:
            result = sol.merge(intervals)
            # Ensure results are sorted for comparison
            assert sorted([list(x) for x in result]) == sorted(expected)
            # print(f"Input: {intervals} -> Passed")
        # print(f"Variant {i} Verified Successfully!\n")

from pathlib import Path
import timeit
import random
import matplotlib.pyplot as plt

def test_benchmark_streaming():
    """Simple test runner to measure performance in streaming case."""
    print("🚀 Starting Streaming Benchmark...")
    sizes = [100, 500, 1000, 2000, 3000]
    results_v2, results_v3 = [], []

    for n in sizes:
        # Make n samples of random data for streaming case.
        raw_data = []
        for _ in range(n):
            lo = random.randint(0, 10000)
            hi = lo + random.randint(1, 100)
            raw_data.append([lo, hi])

        # Get results for v2 "batch-style" approach.
        def run_v2_streaming():
            uut = dim.DynamicIntervalManagementV2()
            current_state = []
            for interval in raw_data:
                current_state.append(interval)
                uut.merge(current_state)
        
        t2 = timeit.timeit(lambda: run_v2_streaming(), number=1)
        results_v2.append(t2)

        # Get results for v3 "tree-style" approach.
        def run_v3_streaming():
            uut = dim.DynamicIntervalManagementV3()
            uut.merge(raw_data)

        t3 = timeit.timeit(lambda: run_v3_streaming(), number=1)
        results_v3.append(t3)
        
        print(f"n={n} | Batch-Style: {t2:.4f}s | Tree-Style: {t3:.4f}s")

    # Write results to console stdout for logging.
    print("| Input Size (N) | Batch-Style (s) | Tree-Style (s) | Speedup |")
    print("| :--- | :--- | :--- | :--- |")
    for i, n in enumerate(sizes):
        speedup = results_v2[i] / results_v3[i]
        print(f"| {n} | {results_v2[i]:.4f} | {results_v3[i]:.4f} | {speedup:.1f}x |")

    # Write results to github summary for viewing.
    write_to_summary(sizes, results_v2, results_v3)

    # Generate Graph
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, results_v2, label='Batch Variant (Two-Pointer)', marker='o', color='red')
    plt.plot(sizes, results_v3, label='Streaming Variant (AVL Tree)', marker='s', color='green')
    plt.title('Streaming Performance: Batch vs. Tree Approaches')
    plt.xlabel('Number of Sequential Intervals (N)')
    plt.ylabel('Total Execution Time (Seconds)')
    plt.legend()
    plt.grid(True)
    file_path = Path("var/artifacts/streaming_performance.png")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(file_path)
    print(f"\n✅ Benchmark complete. Graph saved as '{str(file_path)}'")

# if __name__ == "__main__":
#     # AVL Trees and Deep BSTs can hit the default limit (1000) during 
#     # heavy stress tests/rotations.
#     sys.setrecursionlimit(5000)
    
#     benchmark_static()
#     benchmark_streaming()
