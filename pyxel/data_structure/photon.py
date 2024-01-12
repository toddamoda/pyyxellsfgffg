#  Copyright (c) European Space Agency, 2017.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Photon class to generate and track photon."""

import warnings
from typing import TYPE_CHECKING

import numpy as np
from typing_extensions import override

from pyxel.data_structure import Array

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Photon(Array):
    """Photon class defining and storing information of all photon.

    Accepted array types: ``np.float16``, ``np.float32``, ``np.float64``
    """

    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )
    NAME = "Photon"
    UNIT = "Ph"

    def __init__(self, geo: "Geometry"):
        super().__init__(shape=(geo.row, geo.col))

    @override
    def _get_uninitialized_error_message(self) -> str:
        """Get an explicit error message for an uninitialized 'array'.

        This method is used in the property 'array' in the ``Array`` parent class.
        """
        example_model = "illumination"
        example_yaml_content = """
- name: illumination
  func: pyxel.models.photon_collection.illumination
  enabled: true
  arguments:
      level: 500
      object_center: [250,250]
      object_size: [15,15]
      option: "elliptic"
"""
        cls_name: str = self.__class__.__name__
        obj_name = "photons"
        group_name = "Photon Collection"

        return (
            f"The '.array' attribute cannot be retrieved because the '{cls_name}'"
            " container is not initialized.\nTo resolve this issue, initialize"
            f" '.array' using a model that generates {obj_name} from the "
            f"'{group_name}' group.\n"
            f"Consider using the '{example_model}' model from"
            f" the '{group_name}' group.\n\n"
            "Example code snippet to add to your YAML configuration file "
            f"to initialize the '{cls_name}' container:\n{example_yaml_content}"
        )

    @override
    def _validate(self, value: np.ndarray) -> None:
        """Check that values in array are all positive."""
        if np.any(value < 0):
            value[value < 0] = 0.0
            warnings.warn(
                "Trying to set negative values in the Photon array! Negative values"
                " clipped to 0.",
                stacklevel=2,
            )
        super()._validate(value)
