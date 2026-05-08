import functools
from typing import Any

def validate_args(checks):
    def _validate_args(func):
        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            if len(checks) != len(args):
                raise RuntimeError(f"Checks and args length should be equal. Got {len(checks), len(args)=}")
            for args_index, args_check in enumerate(checks):
                if args_check is not None:
                    args_check(args[args_index])
            return func(*args, **kwargs)
        return _wrapped
    return _validate_args
