#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Type-validation utilities for Pyxel."""

from typing import Annotated, Literal, Union, get_args, get_origin


# ruff: noqa: C901
def check_validity(obj, type_):
    """
    Validate `obj` against `type_`.

    Raises
    ------
        TypeError  – when the Python type is incorrect
        ValueError – when annotated constraints fail
    """

    origin = get_origin(type_)
    args = get_args(type_)

    # ------------------------------------------------------------
    # Annotated[...] — unwrap type and apply metadata constraints
    # ------------------------------------------------------------
    if origin is Annotated:
        base_type, *metadata = args

        # Validate base type
        check_validity(obj, base_type)

        # Apply annotated_types constraints
        for m in metadata:
            # ge (>=)
            if hasattr(m, "ge") and m.ge is not None and obj < m.ge:
                raise ValueError(
                    f"Value {obj!r} is less than the minimum allowed {m.ge!r}"
                )

            # gt (>)
            if hasattr(m, "gt") and m.gt is not None and obj <= m.gt:
                raise ValueError(
                    f"Value {obj!r} must be strictly greater than {m.gt!r}"
                )

            # le (<=)
            if hasattr(m, "le") and m.le is not None and obj > m.le:
                raise ValueError(
                    f"Value {obj!r} is greater than the maximum allowed {m.le!r}"
                )

            # lt (<)
            if hasattr(m, "lt") and m.lt is not None and obj >= m.lt:
                raise ValueError(f"Value {obj!r} must be strictly less than {m.lt!r}")

        return

    # ------------------------------------------------------------
    # Literal[...] — value must be one of specified literals
    # ------------------------------------------------------------
    if origin is Literal:
        if obj not in args:
            raise ValueError(f"Expecting one of {args}. Got {obj!r}")
        return

    # ------------------------------------------------------------
    # Tuple[...] — element-wise validation
    # ------------------------------------------------------------
    if origin is tuple:
        if not isinstance(obj, tuple):
            raise TypeError(f"Expecting a tuple{args}. Got {type(obj).__name__!r}")

        if len(obj) != len(args):
            raise ValueError(f"Expecting tuple of length {len(args)}. Got {len(obj)}")

        for elem, elem_type in zip(obj, args, strict=True):
            check_validity(elem, elem_type)

        return

    # ------------------------------------------------------------
    # Union[...] — value must match at least one type
    # (Used by Optional[T] which is Union[T, None])
    # ------------------------------------------------------------
    if origin is Union:
        for sub_type in args:
            try:
                check_validity(obj, sub_type)
            except Exception:
                pass
            else:
                # No error(s)/exception(s)
                return

        raise TypeError(f"{obj!r} does not match any allowed type {args}")

    # ------------------------------------------------------------
    # Base case: standard Python type check
    # ------------------------------------------------------------
    if not isinstance(obj, type_):
        raise TypeError(f"Expecting a {type_.__name__!r}. Got a {type(obj).__name__!r}")

    return
