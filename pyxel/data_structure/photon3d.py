#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.
"""Pyxel Photon 3D class to generate and track 3D photon."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Optional

import numpy as np
import xarray as xr

from pyxel.util import convert_unit, get_size

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Photon3D:
    """Photon class defining and storing information of all 3d photon. The dimensions are wavelength, y and x.

    Accepted array types: ``np.float16``, ``np.float32``, ``np.float64``
    """

    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )
    NAME = "Photon3d"  # TODO: not used. To remove ?
    UNIT = "Ph/nm"  # TODO: not used. To remove ?

    def __init__(self, geo: "Geometry"):
        self._rows: int = geo.row
        self._cols: int = geo.col

        self._array: Optional[xr.DataArray] = None

    def __eq__(self, other) -> bool:
        return isinstance(other, Photon3D) and (
            (self._array is None and other._array is None)
            or (
                self._array is not None
                and other._array is not None
                and self._array.equals(other._array)
            )
        )

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        if self._array is None:
            dct: Mapping = {"y": self._rows, "x": self._cols}
        else:
            dct = self._array.sizes

        result = ", ".join([f"{key}: {value}" for key, value in dct.items()])
        return f"{cls_name}<{result:s}>"

    def __array__(self, dtype: Optional[np.dtype] = None):
        return np.asarray(self.array, dtype=dtype)

    def empty(self) -> None:
        self._array = None

    def _validate_array(self, value: xr.DataArray) -> None:
        assert isinstance(value, xr.DataArray)
        if value.ndim != 3:
            raise ValueError(
                f"Expected array with 3 dimensions. Got {value.ndim} dimensions."
            )

        if value.dtype not in self.TYPE_LIST:
            raise ValueError(
                f"Expected valid dtype: {', '.join(map(repr, self.TYPE_LIST))}. "
                f"Got dtype: {value.dtype}"
            )

        if value.dims != ("wavelength", "y", "x"):
            raise ValueError(
                "Expected dimensions: 'wavelength', 'y', 'x'. "
                f"Got dimensions: {', '.join(map(repr, value.dims))}"
            )

        shape = (value.sizes["y"], value.sizes["x"])
        if shape != (self._rows, self._cols):
            raise ValueError(
                f"Expected shape {(self._rows,self._cols)!r}. "
                f"Got dimensions: {shape!r}"
            )

    @property
    def array(self) -> xr.DataArray:
        """Three-dimensional numpy array storing the data.

        Only accepts an DataArray with the right type and shape.
        """
        if self._array is None:
            raise ValueError("Property 'array' is not initialized.")

        return self._array

    @array.setter
    def array(self, value: xr.DataArray) -> None:
        """Overwrite the 3-dimensional DataArray storing the data.

        Only accepts an array with the right type and shape.
        """
        self._validate_array(value)
        self._array = value

    def to_xarray(self, dtype: Optional[np.typing.DTypeLike] = None) -> "xr.DataArray":
        if self._array is None:
            new_array = xr.DataArray()
        elif dtype is None:
            new_array = self.array.copy()
        else:
            new_array = self.array.astype(dtype=dtype)

        new_array.name = self.NAME.lower()
        new_array.attrs = {"units": convert_unit(self.UNIT), "long_name": self.NAME}

        return new_array

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using `Pympler` library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes

    def to_dict(self) -> dict:
        if self._array is None:
            return {}
        else:
            return {
                key.replace("/", "#"): value
                for key, value in self.array.to_dict().items()
            }

    # TODO: Remove parameter 'geometry' ?
    # TODO: This method is not used. Remove it.
    @classmethod
    def from_dict(cls, geometry: "Geometry", data: dict) -> "Photon3D":
        new_dct = {key.replace("#", "/"): value for key, value in data.items()}

        array: xr.DataArray = xr.DataArray.from_dict(new_dct)

        obj = cls(geo=geometry)
        obj.array = array

        return obj
