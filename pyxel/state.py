#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
from typing import Any, Optional

__all__ = ["get_obj_att"]


# TODO: Refactor this function ?
def get_obj_att(obj: Any, key: str, obj_type: Optional[type] = None) -> tuple[Any, str]:
    """Retrieve an object associated with a specified key.

    The function is versatile and can be applied to dictionaries, lists,
    or user-defined objects, such as configuration models.

    Parameters
    ----------
    obj : Any
        The target object from which to extract the desired attribute.
    key : str
        A string representing the attribute path within the object.
        Nested attributes are separated by dots.
    obj_type
        An optional parameter specifying the expected type of the retrieved object.
        If provided, the function ensures that the final object matches this type.

    Returns
    -------
    A tuple containing two elements

    1. The object associated with the specified key.
    2. The name of the attribute, extracted from the key.

    Examples
    --------
    >>> obj = {"processor": {"pipeline": {"models": [1, 2, 3]}}}
    >>> get_obj_att(obj, "processor.pipeline.models")
    ({'models': [1, 2, 3]}, 'models')
    """
    *body, tail = key.split(".")
    for part in body:
        try:
            if isinstance(obj, dict):
                obj = obj[part]
            elif isinstance(obj, list):
                try:
                    index = int(part)
                    obj = obj[index]
                except ValueError:
                    for _, obj_i in enumerate(obj):
                        if hasattr(obj_i, part):
                            obj = getattr(obj_i, part)
                            break
                        elif obj_i.__class__.__name__ == part:
                            if hasattr(obj_i, tail):
                                obj = obj_i
                                break
            elif hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise NotImplementedError(
                    f"obj={obj!r}, key={key!r}, obj_type={obj_type!r}, part={part!r}"
                )

            if obj_type and isinstance(obj, obj_type):
                return obj, tail

        except AttributeError:
            # logging.error('Cannot find attribute %r in key %r', part, key)
            obj = None
            break
    return obj, tail
