import data_streaming_accelerators.core.suffix_pattern_recognition as spr

import pytest

@pytest.mark.func
def test_benchmark_static() -> None:
    """Simple test runner to verify all variants."""
    test_cases = [
        # Test Case #1
        [
            ["__init__", "query", "query", "query", "query", "query", "query", "query", "query", "query", "query", "query", "query"],
            [["ec", "ce", "racecar"], ["r"], ["a"], ["c"], ["e"], ["c"], ["a"], ["r"]],
            [None, False, False, False, True, True, False, True]
        ]
    ]
    test_units = [
        # Test Unit #1
        spr.SuffixPatternRecognitionV1
    ]
    for test_unit in test_units:
        for test_case in test_cases:
            uut = None
            for func_name, func_args, expected in zip(*test_case):
                if func_name == "__init__":
                    uut = test_unit(func_args)
                else:
                    result = getattr(uut, func_name)(*func_args)
                    assert result == expected, f"!!! {test_unit=}, : Failed (should be equal): {result=}, {expected=}"
            print(f">>> {test_unit=}: Succeeded")
