#  Copyright (c) European Space Agency, 2017.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Photon class to generate and track photon."""

import warnings
from typing import TYPE_CHECKING, Optional, Self

import numpy as np
import xarray as xr
from typing_extensions import TypeGuard

from pyxel.util import convert_unit, get_size

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


def _is_array_initialized(data: Optional[np.ndarray]) -> TypeGuard[np.ndarray]:
    """Check whether the parameter data is a numpy array.

    Parameters
    ----------
    data : array, Optional
        An optional numpy array.

    Returns
    -------
    bool
        A boolean value indicating whether the array is initialized (not None).

    Notes
    -----
    This function uses special `typing.TypeGuard`.
    This technique is used by static type checkers to narrow type of 'data'.
    For more information, see https://docs.python.org/3/library/typing.html#typing.TypeGuard
    """
    return data is not None


class Photon:
    """Photon class defining and storing information of all photon.

    Accepted array types: ``np.float16``, ``np.float32``, ``np.float64``
    """

    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )
    # NAME = "Photon"
    # UNIT = "Ph"

    def __init__(self, geo: "Geometry"):
        self._array_2d: Optional[np.ndarray] = None
        self._array_3d: Optional[xr.DataArray] = None

        self._shape_2d = geo.row, geo.col

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        if self._array_2d is None and self._array_3d is None:
            return f"{cls_name}<UNINITIALIZED, shape={self.shape}>"

        elif self._array_2d is not None and self._array_3d is None:
            return f"{cls_name}<shape={self.shape}, dtype={self.dtype}>"

        elif self._array_2d is None and self._array_3d is not None:
            dct = self._array_3d.sizes
            result = ", ".join([f"{key}: {value}" for key, value in dct.items()])
            return f"{cls_name}<{result:s}>"

        else:
            raise NotImplementedError

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and (
                self._array_2d is not None
                and np.array_equal(self._array_2d, other._array_2d)
            )
            and xr.DataArray.equals(self._array_3d, other._array_3d)
        )

    def __array__(self, dtype: Optional[np.dtype] = None):
        if self._array_2d is None and self._array_3d is None:
            return ValueError("Not initialized")
        elif self._array_2d is not None:
            return np.asarray(self._array_2d, dtype=dtype)
        elif self._array_3d is not None:
            return np.array(self._array_3d, dtype=dtype)
        else:
            return NotImplementedError

    def __iadd__(self, other: np.ndarray):
        if not isinstance(other, np.ndarray):
            raise TypeError

        if self._array_2d is not None:
            self._array_2d += other
        else:
            self._array_2d = other
        return self

    def __add__(self, other: np.ndarray):
        if not isinstance(other, np.ndarray):
            raise TypeError

        if self._array_2d is not None:
            self._array_2d += other
        else:
            self._array_2d = other
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
        if self._array_2d is None and self._array_3d is None:
            return tuple()
        elif self._array_2d is not None:
            return self._array_2d.shape
        elif self._array_3d is not None:
            return self._array_3d.shape
        else:
            raise NotImplementedError

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def dtype(self) -> np.dtype:
        if self._array_2d is None and self._array_3d is None:
            raise ValueError("Not initialized")
        elif self._array_2d is not None:
            return self._array_2d.dtype
        elif self._array_3d is not None:
            return self._array_3d.dtype
        else:
            raise NotImplementedError

    @property
    def array(self) -> np.ndarray:
        """Two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.

        Raises
        ------
        ValueError
            Raised if 'array' is not initialized.
        """
        if not _is_array_initialized(self._array_2d):
            msg: str = self._get_uninitialized_error_message()
            raise ValueError(msg)

        return self._array_2d

    @array.setter
    def array(self, value: np.ndarray) -> None:
        """Overwrite the two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.
        """
        cls_name: str = self.__class__.__name__

        if not isinstance(value, np.ndarray):
            raise TypeError(f"{cls_name} array should be a numpy.ndarray")

        if value.dtype not in self.TYPE_LIST:
            raise TypeError(
                f"Expected types of {cls_name} array are "
                f"{', '.join(map(str, self.TYPE_LIST))}."
            )

        if value.shape != self._shape_2d:
            raise ValueError(f"Expected {cls_name} array is {self._shape_2d}.")

        if np.any(value < 0):
            value[value < 0] = 0.0
            value = np.clip(value, a_min=0.0, a_max=None)
            warnings.warn(
                "Trying to set negative values in the Photon array! Negative values"
                " clipped to 0.",
                stacklevel=2,
            )

        self._array_2d = value

    @property
    def array3d(self) -> xr.DataArray:
        raise NotImplementedError

    @array3d.setter
    def array3d(self, value: xr.DataArray) -> None:
        if not isinstance(value, xr.DataArray):
            raise TypeError("Expecting a 'DataArray'.")

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
        if shape != self._shape_2d:
            raise ValueError(
                f"Expected shape {self._shape_2d!r}. Got dimensions: {shape!r}"
            )

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using `Pympler` library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        if self._array_2d is None and self._array_3d is None:
            return 0
        elif self._array_2d is not None and self._array_3d is None:
            return get_size(self._array_2d)
        elif self._array_2d is None and self._array_3d is not None:
            return get_size(self._array_3d)
        else:
            raise NotImplementedError

    def to_dict(self) -> dict:
        if self._array_2d is None and self._array_3d is None:
            return {}
        elif self._array_2d is not None and self._array_3d is None:
            raise NotImplementedError
        elif self._array_2d is None and self._array_3d is not None:
            return {
                "array_3d": {
                    key.replace("/", "#"): value
                    for key, value in self._array_3d.to_dict().items()
                }
            }
        else:
            raise NotImplementedError

    @classmethod
    def from_dict(cls, geometry: "Geometry", data: dict) -> Self:
        array_2d: Optional[np.ndarray] = None
        if "array_2d" in data:
            raise NotImplementedError

        array_3d: Optional[xr.DataArray] = None
        if "array_3d" in data:
            dct_array_3d = data.get("array_3d", dict())
            new_dct = {
                key.replace("#", "/"): value for key, value in dct_array_3d.items()
            }

            array_3d = xr.DataArray.from_dict(new_dct)

        obj = cls(geo=geometry)
        obj._array_2d = array_2d
        obj._array_3d = array_3d

        return obj

    def to_xarray(self, dtype: Optional[np.typing.DTypeLike] = None) -> xr.DataArray:
        if self._array_2d is None and self._array_3d is None:
            return xr.DataArray()
        elif self._array_2d is not None and self._array_3d is None:
            num_rows, num_cols = self.shape

            return xr.DataArray(
                np.array(self.array, dtype=dtype),
                name="photon",
                dims=["y", "x"],
                coords={"y": range(num_rows), "x": range(num_cols)},
                attrs={"units": convert_unit("Ph"), "long_name": "Photon"},
            )

        elif self._array_2d is None and self._array_3d is not None:
            new_array = self._array_3d.astype(dtype=dtype)

            new_array.name = "photon3d"
            new_array.attrs = {"units": convert_unit("Ph/nm"), "long_name": "Photon 3D"}

            return new_array

        else:
            raise NotImplementedError

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

    def empty(self):
        self._array_2d = None
        self._array_3d = None
