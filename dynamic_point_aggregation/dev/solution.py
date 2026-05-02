""" # Design Summary:
    - Intuition:
        - For dynamic point aggregation with disjoint intervals,
            new values are either enclosed by, adjacent to, or distinct from
            the existing intervals already formed from stream history.
"""

class DynamicPointAggregationV1:
    """ # Design Details:
        - Approach:
            - V1 The naive approach updates an unsorted set to add new values
            and uses the sweep line method to find intervals.
            - Built-in types set and list have low bytecode overhead.
        - Complexity:
            - __init__: Runtime O(1). Memory O(1).
            - addNum: Runtime O(1). Memory O(1).
            - getIntervals: Runtime O(N Log N). Memory O(N).
    
        # Static Benchmarks:
        - Results:
            - 1. Runtime 0 ms (*100%). Memory 19.53 MB (*38%).
            - 2. Runtime 0 ms (*100%). Memory 19.48 MB (*72%).
            - 3. Runtime 0 ms (*100%). Memory 19.58 MB (*38%).
    """

    def __init__(self):
        """Make new object for dynamic point aggregation api.
        Takes runtime O(1) and memory O(1)."""
        self._points = set()

    def addNum(self, value: int) -> None:
        """Add new value to stream history if not already added.
        Takes runtime O(1) and memory O(1)."""
        self._points.add(value)  # ignores duplicates

    def getIntervals(self) -> list[list[int]]:
        """Make interval sequence from stream history.
        Takes runtime O(N Log N) and memory O(N)."""
        if not self._points: return []  # skip if empty
        intervals = []; sorted_points = sorted(self._points)
        a = b = 0; point_a = point_b = sorted_points[0]
        for c in range(1, len(sorted_points)):
            point_c = sorted_points[c]
            if point_c == point_b+1:
                b = c; point_b = point_c; continue
            intervals.append([point_a, point_b])
            a = b = c; point_a = point_b = point_c
        intervals.append([point_a, point_b])
        return intervals

from sortedcontainers import SortedSet

class DynamicPointAggregationV2:
    """ # Design Details:
        - Approach:
            - V2 The efficient approach updates 2 sorted sets to add new values
            and uses the binary search method to find intervals.
            - Although third party type SortedSet has high bytecode overhead,
            the trade-off of performance for readability is worth it here.
        - Complexity:
            - __init__: Runtime O(1). Memory O(1).
            - addNum: Runtime O(Sqrt N). Memory O(1).
            - getIntervals:  Runtime O(N). Memory O(N).
    
        # Static Benchmarks:
        - Results:
            - 1. Runtime 0 ms (*100%). Memory 19.65 MB (*13).
            - 2. Runtime 3 ms (*16%). Memory 19.62 MB (*13).
            - 3. Runtime 3 ms (*16%). Memory 19.67 MB (*13).
    """

    def __init__(self):
        """Make new object for dynamic point aggregation api.
        Takes runtime O(1) and memory O(1)."""
        self._lower_bounds = SortedSet()
        self._upper_bounds = SortedSet()
        self._bounds_total = 0

    def addNum(self, value: int) -> None:
        """Add new value to stream history if not already added.
        Takes runtime O(Sqrt N) and memory O(1)."""
        _lower_bounds, _upper_bounds = self._lower_bounds, self._upper_bounds
        _bounds_total = self._bounds_total

        # 1. Find the lower bounds in sorted set using binary search.
        # Takes runtime O(Log N) and memory O(1).
        ip_lower_bounds = -1
        if (_ip := _lower_bounds.bisect_right(value)) != 0:
            ip_lower_bounds = _ip-1
            if _lower_bounds[ip_lower_bounds] == value: return

        # 2. Find the upper bounds in sorted set at nearby indices.
        # In theory, takes runtime O(1) and memory O(1).
        # With sortedcontainers indexing, takes runtime O(Log N) and memory O(1).
        ip_upper_bounds = _bounds_total
        if (_ip := ip_lower_bounds) != -1 \
        and _upper_bounds[_ip] >= value:
            ip_upper_bounds = _ip
            if _upper_bounds[ip_upper_bounds] == value: return
        elif (_ip := ip_lower_bounds+1) != _bounds_total \
        and _upper_bounds[_ip] >= value:
            ip_upper_bounds = _ip
            if _upper_bounds[ip_upper_bounds] == value: return
        if ip_lower_bounds == ip_upper_bounds: return

        # 3. Update sorted set to merge adjacent intervals.
        # In theory, takes runtime O(Log N) and memory O(1).
        # With sortedcontainers add/remove, takes runtime O(Sqrt N) and memory O(1).
        is_adjacent_to_next = (
            (0 <= ip_lower_bounds+1 <= _bounds_total-1
             and _lower_bounds[ip_lower_bounds+1] == value+1)
        )
        is_adjacent_to_prev = (
            (0 <= ip_upper_bounds-1 <= _bounds_total-1
             and _upper_bounds[ip_upper_bounds-1] == value-1)
        )
        if is_adjacent_to_next and is_adjacent_to_prev:
            self._lower_bounds.remove(value+1)
            self._upper_bounds.remove(value-1)
            self._bounds_total -= 1
        elif is_adjacent_to_next:
            self._lower_bounds.remove(value+1)
            self._lower_bounds.add(value)
        elif is_adjacent_to_prev:
            self._upper_bounds.remove(value-1)
            self._upper_bounds.add(value)
        else:
            self._lower_bounds.add(value)
            self._upper_bounds.add(value)
            self._bounds_total += 1

    def getIntervals(self) -> list[list[int]]:
        """Make interval sequence from stream history.
        Takes runtime O(N) and memory O(N)."""
        return [
            list(pair) for pair in zip(self._lower_bounds, self._upper_bounds)
        ]

def benchmark_static():
    """Simple test runner to verify all variants."""
    test_cases = [
        [
            # test_name
            "Test Case 1: Empty Stream",
            # func_name
            ["__init__", "getIntervals"],
            # func_args
            [[], []],
            # func_returns
            [None, []]
        ],
        [
            # test_name
            "Test Case 2: Merge Adjacent Intervals",
            # func_name
            ["__init__", "addNum", "addNum", "addNum", "getIntervals"],
            # func_args
            [[], [1], [3], [2], []],
            # expec_returns
            [None, None, None, None, [[1, 3]]]
        ],
        [
            # test_name
            "Test Case 3: Merge Enclosed Intervals",
            # func_name
            ["__init__", "addNum", "addNum", "addNum", "addNum", "addNum", "addNum", "getIntervals"],
            # func_args
            [[], [1], [3], [2], [1], [3], [2], []],
            # expec_returns
            [None, None, None, None, None, None, None, [[1, 3]]]
        ],
        [
            # test_name
            "Test Case 4: Merge Distinct Intervals",
            # func_name
            ["__init__", "addNum", "addNum", "addNum", "getIntervals"],
            # func_args
            [[], [1], [3], [7], []],
            # expec_returns
            [None, None, None, None, [[1, 1], [3, 3], [7, 7]]]
        ],
    ]
    test_units = [
        DynamicPointAggregationV1,
        DynamicPointAggregationV2,
    ]
    for test_unit in test_units:
        for test_case in test_cases:
            test_name = test_case[0]; uut = None
            for _, func_name, func_args, expec_returns in zip(*test_case):
                if func_name == "__init__":
                    uut = test_unit(*func_args)
                else:
                    returns = getattr(uut, func_name)(*func_args)
                    assert returns == expec_returns, f"!!! {test_unit=}, {test_name=}: Failed (should be equal): {returns=}, {expec_returns=}"
            print(f">>> {test_name=}: Succeeded")
        print(f">>> {test_unit=}: Succeeded")

import itertools
import os
import random
import timeit

def log_summary(line, sink=print):
    """Simple log emission for a summary line."""

    # Write results to console stdout for logging.
    sink(line)

    # Write results to github summary for viewing.
    if (summary_file := os.getenv('GITHUB_STEP_SUMMARY')):
        with open(summary_file, 'a') as f:
            f.write(line)

from matplotlib import pyplot as plt
import pandas as pd

def benchmark_streaming():
    """Simple test runner to validate all variants."""

    data_sizes = [100, 200, 500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000]
    request_distrs = [0.10, 0.20, 0.50, 0.80]
    test_cases = list(itertools.product(data_sizes, request_distrs))
    test_units = [
        DynamicPointAggregationV1,
        DynamicPointAggregationV2,
    ]
    log_header = [
        "TestCaseID",
        "DataSize",
        "RequestDistribution",
        "V1TimeElapsed",
        "V2TimeElapsed",
        "SpeedupV1V2",
        "SpeedupV2V1",
    ]
    log_summary("| " + " | ".join(log_header) + " |")
    log_summary("| " + " | ".join([":---"] * len(log_header)) + " |")

    def _events(data_size, request_distr):
        random.seed(42)  # reproducible results
        data_size_sent = 0
        while data_size_sent < data_size:
            if random.random() < request_distr:
                yield ["getIntervals", []]
            else:
                data_size_sent += 1
                yield ["addNum", [random.randint(0, 10000)]]

    def _harness(uut, events):
        for func_name, func_args in events:
            getattr(uut, func_name)(*func_args)

    test_results = [0] * len(test_cases)
    for test_case_id, test_case in enumerate(test_cases):
        data_size, request_distr = test_case
        time_elapsed = [
            timeit.timeit(lambda: _harness(test_unit(), _events(data_size, request_distr)), number=1)
            for test_unit in test_units
        ]
        test_case_results = [
            # "TestCaseID",
            test_case_id,
            # "DataSize",
            data_size,
            # "RequestDistribution",
            request_distr,
            # "V1TimeElapsed",
            time_elapsed[0],
            # "V2TimeElapsed",
            time_elapsed[1],
            # "SpeedupV1V2",
            time_elapsed[1] / time_elapsed[0],
            # "SpeedupV2V1",
            time_elapsed[0] / time_elapsed[1],
        ]
        log_test_case = [
            f"{test_case_results[0]:d}",
            f"{test_case_results[1]:d}",
            f"{test_case_results[2]:.3f}",
            f"{test_case_results[3]:.3f}",
            f"{test_case_results[4]:.3f}",
            f"{test_case_results[5]:.3f}",
            f"{test_case_results[6]:.3f}",
        ]
        log_summary("| " + " | ".join(log_test_case) + " |")
        test_results[test_case_id] = test_case_results

    def _generate_graph(results):
        nonlocal log_header
        df = pd.DataFrame(results, columns=log_header)

        # Graph 1: Speedup by Data Size
        ndigits_dec = max(len(str(x).split(".")[1]) for x in df["RequestDistribution"])
        for request_distr in df["RequestDistribution"].unique():
            _df = df[df["RequestDistribution"] == request_distr]
            graph_title = f'Speedup by Data Size (R={request_distr})'
            file_name = f'speedup_by_data_size_request_distr{request_distr:0.{ndigits_dec}f}.png'

            fig, ax1 = plt.subplots()
            ax1.plot(
                _df["DataSize"],
                _df["V1TimeElapsed"],
                label="Batch V1",
                marker="o",
                color="blue",
            )
            ax1.plot(
                _df["DataSize"],
                _df["V2TimeElapsed"],
                label="Streaming V2",
                marker="o",
                color="green",
            )
            ymax = max(max(_df["V1TimeElapsed"]), max(_df["V2TimeElapsed"]))
            ax1.set_ylim(0, 1.2*ymax)  # add headroom for legend
            ax1.set_ylabel("Time Elapsed (sec)")
            ax1.set_xlabel("Data Size (N)")

            ax2 = ax1.twinx()
            ax2.plot(
                _df["DataSize"],
                _df["SpeedupV2V1"],
                linestyle="--",
                linewidth=2,
                label="Speedup V2/V1",
                color="red",
            )
            ymax = max(_df["SpeedupV2V1"])
            ax2.set_ylim(0, 1.2*ymax)  # add headroom for legend
            ax2.set_ylabel("Speedup V2/V1 (Gain)")

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

            plt.title(graph_title); plt.grid(True); plt.tight_layout()
            plt.savefig(file_name); plt.close(fig)
            log_summary(f"created {file_name=}")

        # Graph 2: Speedup by Request Distribution
        ndigits_int = max(len(str(x)) for x in df["DataSize"])
        for data_size in df["DataSize"].unique():
            _df = df[df["DataSize"] == data_size]
            graph_title = f'Speedup by Request Distribution (N={data_size})'
            file_name = f'speedup_by_request_distr_data_size_{data_size:0{ndigits_int}d}.png'

            fig, ax1 = plt.subplots()
            ax1.plot(
                _df["RequestDistribution"],
                _df["V1TimeElapsed"],
                label="Batch V1",
                marker="o",
                color="blue",
            )
            ax1.plot(
                _df["RequestDistribution"],
                _df["V2TimeElapsed"],
                label="Streaming V2",
                marker="o",
                color="green",
            )
            ymax = max(max(_df["V1TimeElapsed"]), max(_df["V2TimeElapsed"]))
            ax1.set_ylim(0, 1.2*ymax)  # add headroom for legend
            ax1.set_ylabel("Time Elapsed (sec)")
            ax1.set_xlabel("Request Distribution (R)")

            ax2 = ax1.twinx()
            ax2.plot(
                _df["RequestDistribution"],
                _df["SpeedupV2V1"],
                linestyle="--",
                linewidth=2,
                label="Speedup V2/V1",
                color="red",
            )
            ymax = max(_df["SpeedupV2V1"])
            ax2.set_ylim(0, 1.2*ymax)  # add headroom for legend
            ax2.set_ylabel("Speedup V2/V1 (Gain)")

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

            plt.title(graph_title); plt.grid(True); plt.tight_layout()
            plt.savefig(file_name); plt.close(fig)
            log_summary(f"created {file_name=}")

    _generate_graph(test_results)

if __name__ == "__main__":
    benchmark_static()
    benchmark_streaming()
