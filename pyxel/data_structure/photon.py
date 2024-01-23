#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Photon class to generate and track photon."""

import warnings
from collections.abc import Hashable, Mapping
from typing import TYPE_CHECKING, Any, Optional, Self, Union

import numpy as np
import xarray as xr

from pyxel.util import convert_unit, get_size

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Photon:
    """Photon class defining and storing information of all photon.

    Accepted array types: ``np.float16``, ``np.float32``, ``np.float64``
    """

    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )

    def __init__(self, geo: "Geometry"):
        self._array: Union[np.ndarray, xr.DataArray, None] = None

        self._num_rows: int = geo.row
        self._num_cols: int = geo.col

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        if self._array is None:
            return f"{cls_name}<UNINITIALIZED, shape={self.shape}>"

        elif isinstance(self._array, np.ndarray):
            return f"{cls_name}<shape={self.shape}, dtype={self.dtype}>"

        elif isinstance(self._array, xr.DataArray):
            dct = self._array.sizes
            result = ", ".join([f"{key}: {value}" for key, value in dct.items()])
            return f"{cls_name}<{result:s}>"

        else:
            raise NotImplementedError

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return False

        if self._array is other._array is None:
            return True

        if isinstance(self._array, np.ndarray):
            return np.array_equal(self._array, other._array)

        if isinstance(self._array, xr.DataArray):
            return self._array.equals(other._array)

        return False

    def __array__(self, dtype: Optional[np.dtype] = None) -> np.ndarray:
        if self._array is None:
            raise ValueError("Not initialized")

        return np.asarray(self._array, dtype=dtype)

    def __iadd__(self, other: Union[np.ndarray, xr.DataArray]) -> Self:
        if isinstance(other, np.ndarray) and isinstance(self._array, xr.DataArray):
            raise TypeError("Must be a DataArray")

        if isinstance(other, xr.DataArray) and isinstance(self._array, np.ndarray):
            raise TypeError("Must be a numpy array")

        if self._array is not None:
            self._array += other
        else:
            self._array = other
        return self

    def __add__(self, other: Union[np.ndarray, xr.DataArray]) -> Self:
        if isinstance(other, np.ndarray) and isinstance(self._array, xr.DataArray):
            raise TypeError("Must be a DataArray")

        if isinstance(other, xr.DataArray) and isinstance(self._array, np.ndarray):
            raise TypeError("Must be a numpy array")

        if self._array is not None:
            self._array += other
        else:
            self._array = other
        return self

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

    @property
    def shape(self) -> tuple[int, ...]:
        if self._array is None:
            return ()

        return self._array.shape

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def dtype(self) -> np.dtype:
        if self._array is None:
            raise ValueError("Not initialized")

        return self._array.dtype

    @property
    def array(self) -> Union[np.ndarray, xr.DataArray]:
        """Two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.

        Raises
        ------
        ValueError
            Raised if 'array' is not initialized.
        """
        if self._array is None:
            msg: str = self._get_uninitialized_error_message()
            raise ValueError(msg)

        return self._array

    @array.setter
    def array(self, value: Union[np.ndarray, xr.DataArray]) -> None:
        """Overwrite the two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.
        """
        cls_name: str = self.__class__.__name__

        if not isinstance(value, (np.ndarray, xr.DataArray)):
            raise TypeError(f"{cls_name} array must be a numpy.ndarray or xr.DataArray")

        if value.dtype not in self.TYPE_LIST:
            raise ValueError(
                f"{cls_name} array 'dtype' must be one of these values: "
                f"{', '.join(map(str, self.TYPE_LIST))}. Got {value.dtype!r}"
            )

        if isinstance(value, np.ndarray):
            if value.ndim != 2:
                raise ValueError(
                    f"{cls_name} array must have 2 dimensions. Got: {value.ndim}"
                )

            if value.shape != (self._num_rows, self._num_cols):
                raise ValueError(
                    f"{cls_name} array must have this shape: {(self._num_rows, self._num_cols)!r}. Got: {(self._num_rows, self._num_cols)!r}"
                )

        elif isinstance(value, xr.DataArray):
            if value.ndim != 3:
                raise ValueError(
                    f"{cls_name} data array must have 3 dimensions. Got: {value.ndim}"
                )

            expected_dims = ("wavelength", "y", "x")
            if value.dims != expected_dims:
                raise ValueError(
                    f"{cls_name} data array must have these dimensions: {expected_dims!r}. Got: {value.dims!r}"
                )

            shape_3d: Mapping[Hashable, int] = value.sizes
            if (shape_3d["y"], shape_3d["x"]) != (self._num_rows, self._num_cols):
                raise ValueError(
                    f"{cls_name} data array must have this shape: {(self._num_rows, self._num_cols)!r}. Got: {self.shape!r}"
                )

            if "wavelength" not in value.coords:
                raise ValueError(
                    f"{cls_name} data array must have coordinates for dimension 'wavelength'."
                )

        if np.any(value < 0):
            value = np.clip(value, a_min=0.0, a_max=None)
            warnings.warn(
                "Trying to set negative values in the Photon array! Negative values"
                " clipped to 0.",
                stacklevel=4,
            )

        self._array = value.copy()

    @property
    def array_2d(self) -> np.ndarray:
        """Two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.

        Raises
        ------
        ValueError
            Raised if 'array' is not initialized.
        """
        if self._array is None:
            msg: str = self._get_uninitialized_error_message()
            raise ValueError(msg)

        if not isinstance(self._array, np.ndarray):
            raise TypeError

        return self._array

    @property
    def array_3d(self) -> xr.DataArray:
        """Three-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.

        Raises
        ------
        ValueError
            Raised if 'array' is not initialized.
        """
        if self._array is None:
            msg: str = self._get_uninitialized_error_message()
            raise ValueError(msg)

        if not isinstance(self._array, xr.DataArray):
            raise TypeError

        return self._array

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using `Pympler` library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        if self._array is None:
            return 0

        return get_size(self._array)

    def to_dict(self) -> dict:
        dct: dict = {}
        if self._array is None:
            # Do nothing
            pass

        elif isinstance(self._array, np.ndarray):
            dct["array_2d"] = self._array.copy()

        elif isinstance(self._array, xr.DataArray):
            dct["array_3d"] = {
                key.replace("/", "#"): value
                for key, value in self._array.to_dict().items()
            }

        else:
            raise NotImplementedError

        return dct

    @classmethod
    def from_dict(cls, geometry: "Geometry", data: Mapping[str, Any]) -> Self:
        obj = cls(geo=geometry)

        if "array_2d" in data:
            obj.array = np.array(data["array_2d"])

        elif "array_3d" in data:
            dct_array_3d = data.get("array_3d", dict())
            new_dct = {
                key.replace("#", "/"): value for key, value in dct_array_3d.items()
            }

            obj.array = xr.DataArray.from_dict(new_dct)

        return obj

    def to_xarray(self, dtype: Optional[np.typing.DTypeLike] = None) -> xr.DataArray:
        if self._array is None:
            return xr.DataArray()

        if isinstance(self._array, np.ndarray):
            num_rows, num_cols = self.shape

            return xr.DataArray(
                np.array(self.array, dtype=dtype),
                name="photon",
                dims=["y", "x"],
                coords={"y": range(num_rows), "x": range(num_cols)},
                attrs={"units": convert_unit("Ph"), "long_name": "Photon"},
            )

        else:
            data_3d: xr.DataArray = self._array.astype(dtype=dtype)
            data_3d.name = "photon"
            data_3d.coords["y"] = range(self._num_rows)
            data_3d.coords["x"] = range(self._num_cols)
            data_3d.attrs = {"units": convert_unit("Ph/nm"), "long_name": "Photon"}

            return data_3d

    def plot(self, robust: bool = True) -> None:
        """Plot the array using Matplotlib.

        Parameters
        ----------
        robust : bool, optional
            If True, the colormap is computed with 2nd and 98th percentile
            instead of the extreme values.

        Examples
        --------
        >>> detector.photon.plot()

        .. image:: _static/photon_plot.png
        """
        arr: xr.DataArray = self.to_xarray()

        return arr.plot(robust=robust)

    def empty(self) -> None:
        self._array = None
