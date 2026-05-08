import data_streaming_accelerators.common.validators as validators

import pytest
from contextlib import nullcontext

_returns_none = lambda _: None
_returns_true = lambda _: True

@pytest.mark.func
@pytest.mark.parametrize(
    "checks, func, args, expectation",
    [
        ([_returns_none], _returns_true, [], pytest.raises(RuntimeError)),
        ([], _returns_true, [True], pytest.raises(RuntimeError)),
        ([_returns_none], _returns_true, [True], nullcontext()),
    ]
)
def test_validate_args(checks, func, args, expectation):
    with expectation as exp:
        assert validators.validate_args(checks)(func)(*args)
