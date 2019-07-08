"""Subpackage containing several checkers."""

import os
import typing as t

import esapy_config.checkers as checkers

__all__ = ['check_path', 'check_type', 'check_range', 'check_choices']


def check_path(path):
    """TBW."""
    return os.path.exists(path)


def check_type(att_type, is_optional: bool = False) -> t.Callable[..., bool]:
    """TBW."""
    return checkers.check_type_function(att_type=att_type, is_optional=is_optional)


def check_range(min_val: t.Union[float, int], max_val: t.Union[float, int]):
    """TBW."""
    return checkers.check_range(min_val=min_val,
                                max_val=max_val,
                                step=None, enforce_step=False)
    # todo: rounding BUG in checkers.check_range() when value is a float!


def check_choices(choices: list):
    """TBW."""
    return checkers.check_choices(choices)
