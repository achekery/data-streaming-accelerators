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
    
        # Result:
        - Benchmark:
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
    
        # Result:
        - Benchmark:
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
                    assert returns == expec_returns, f"!!! {test_unit=}, : Failed (should be equal): {returns=}, {expec_returns=}"
            print(f">>> {test_name=}: Succeeded")
        print(f">>> {test_unit=}: Succeeded")

import itertools
import os
import random
import timeit

from matplotlib import pyplot as plt
import pandas as pd

def benchmark_streaming():
    """Simple test runner to validate all variants."""

    def _log_emitter(line, sink=print):
        # Write results to console stdout for logging.
        sink(line)
        # Write results to github summary for viewing.
        if (summary_file := os.getenv('GITHUB_STEP_SUMMARY')):
            with open(summary_file, 'a') as f:
                f.write(line)

    data_sizes = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000]
    usage_ratios = [1, 2, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    test_cases = list(itertools.product(data_sizes, usage_ratios))
    test_units = [
        DynamicPointAggregationV1,
        DynamicPointAggregationV2,
    ]
    log_header = [
        "TestCase",
        "DataSize",
        "UsageRatio",
        "V1ElapsedSec",
        "V2ElapsedSec",
        "SpeedupV2V1",
    ]
    _log_emitter("| " + " | ".join(log_header) + " |")
    _log_emitter("| " + " | ".join([":---"] * len(log_header)) + " |")

    all_results = [0] * len(test_cases)
    for test_case_id, test_case in enumerate(test_cases):
        data_size, usage_ratio = test_case
        test_units_timed = [0] * len(test_units)
        for test_unit_id, test_unit in enumerate(test_units):
            uut = test_unit()

            def _events():
                nonlocal data_size; nonlocal usage_ratio
                random.seed(42)  # reproducible results
                for i in range(data_size):
                    # sent get request once every `usage_ratio` events
                    if usage_ratio != 0 and i % usage_ratio == 0:
                        yield ["getIntervals", []]
                    # send add request otherwise
                    else:
                        yield ["addNum", [random.randint(0, 10000)]]

            def _harness(events):
                nonlocal uut
                for func_name, func_args in events:
                    getattr(uut, func_name)(*func_args)

            timed = timeit.timeit(lambda: _harness(_events()), number=1)
            test_units_timed[test_unit_id] = timed

        test_case_results = [
            test_case_id,
            data_size,
            usage_ratio,
            test_units_timed[0], # v1 elapsed
            test_units_timed[1], # v2 elapsed
            test_units_timed[1] / test_units_timed[0]  # speedup
        ]
        log_test_case = [
            f"{test_case_results[0]:d}",
            f"{test_case_results[1]:d}",
            f"{test_case_results[2]:d}",
            f"{test_case_results[3]:.3f}",
            f"{test_case_results[4]:.3f}",
            f"{test_case_results[5]:.3f}",
        ]
        _log_emitter("| " + " | ".join(log_test_case) + " |")
        all_results[test_case_id] = test_case_results

    def _generate_graph(results):
        nonlocal data_sizes; nonlocal usage_ratios
        n_data_sizes = len(data_sizes)
        n_usage_ratios = len(usage_ratios)

        df = pd.DataFrame(results, columns=log_header)

        # group by data size
        for i, data_size in enumerate(data_sizes):
            _df = df[df["DataSize"] == data_size]

            fig, ax1 = plt.subplots()
            ax1.plot(
                _df["UsageRatio"],
                _df["V1ElapsedSec"],
                label="Batch Variant V1 (sec)",
                marker="o",
                color="blue",
            )
            ax1.plot(
                _df["UsageRatio"],
                _df["V2ElapsedSec"],
                label="Streaming Variant V2 (sec)",
                marker="+",
                color="green",
            )
            ax1.set_ylabel("Elapsed Time (sec)")
            ax1.set_xlabel("Usage Ratio R (%)")
            ax1.legend(loc="lower right")

            ax2 = ax1.twinx()
            ax2.plot(
                _df["UsageRatio"],
                _df["SpeedupV2V1"],
                label="Speedup V2/V1",
                marker="x",
                color="red",
            )
            ax2.set_ylabel("Speedup V2/V1 (Gain)")
            ax2.legend(loc="upper right")

            plt.show()
            plt.title(f'Streaming (N={data_size}): Speedup by Usage Ratio R')
            plt.grid(True)
            plt.savefig(f'streaming_data_size_{data_size}.png')


        # group by usage ratio
        for i, usage_ratio in enumerate(usage_ratios):
            _df = df[df["UsageRatio"] == usage_ratio]

            fig, ax1 = plt.subplots()
            ax1.plot(
                _df["DataSize"],
                _df["V1ElapsedSec"],
                label="Batch Variant V1 (sec)",
                marker="o",
                color="blue",
            )
            ax1.plot(
                _df["DataSize"],
                _df["V2ElapsedSec"],
                label="Streaming Variant V2 (sec)",
                marker="+",
                color="green",
            )
            ax1.set_ylabel("Elapsed Time (sec)")
            ax1.set_xlabel("Data Size (N)")
            ax1.legend(loc="lower right")

            ax2 = ax1.twinx()
            ax2.plot(
                _df["DataSize"],
                _df["SpeedupV2V1"],
                label="Speedup V2/V1",
                marker="x",
                color="red",
            )
            ax2.set_ylabel("Speedup V2/V1 (Gain)")
            ax2.legend(loc="upper right")

            plt.show()
            plt.title(f'Streaming (R={usage_ratio}): Speedup by Data Size')
            plt.grid(True)
            plt.savefig(f'streaming_usage_ratio_{usage_ratio}.png')



    # _generate_graph(all_results)
    # TODO: Enable once we know what data to show

if __name__ == "__main__":
    benchmark_static()
    benchmark_streaming()
