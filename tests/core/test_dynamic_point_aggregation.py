import data_streaming_accelerators.core.dynamic_point_aggregation as dpa

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

def test_benchmark_static():
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
        dpa.DynamicPointAggregationV1,
        dpa.DynamicPointAggregationV2,
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

from pathlib import Path

from matplotlib import pyplot as plt
import pandas as pd

def test_benchmark_streaming():
    """Simple test runner to validate all variants."""

    data_sizes = [100, 200, 500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000]
    request_distrs = [0.10, 0.20, 0.50, 0.80]
    test_cases = list(itertools.product(data_sizes, request_distrs))
    test_units = [
        dpa.DynamicPointAggregationV1,
        dpa.DynamicPointAggregationV2,
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

        dir_path = Path("var/artifacts/test_dynamic_point_aggregation")
        dir_path.mkdir(parents=True, exist_ok=True)

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
            plt.savefig(dir_path / file_name); plt.close(fig)
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
            plt.savefig(dir_path / file_name); plt.close(fig)
            log_summary(f"created {file_name=}")

    _generate_graph(test_results)
