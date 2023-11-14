#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Array class."""

from typing import TYPE_CHECKING, Optional, Union

import numpy as np

from pyxel.util import convert_unit, get_size

if TYPE_CHECKING:
    import xarray as xr


# TODO: Is it possible to move this to `data_structure/__init__.py' ?
# TODO: Does it make sense to force 'self._array' to be read-only ?
#       It could be done with:
#       ... self._array = np.array(value)
#       ... self._array.setflags(write=False)
class Array:
    """Array class."""

    EXP_TYPE: Union[type, np.dtype] = type(None)
    TYPE_LIST: tuple[np.dtype, ...] = ()
    NAME: str = ""
    UNIT: str = ""

    # TODO: Add units ?
    def __init__(self, shape: Optional[tuple[int, int]] = None):
        # if value is None and shape is None:
        #     raise ValueError("Invalid arguments to Array initializer.")
        #
        # if value is not None:
        #     if value.ndim != 2:
        #         raise ValueError(
        #             f"Expecting a 2D array. Got an array with {value.ndim} dimensions."
        #         )
        #
        #     self.validate_type(value)
        #     shape = value.shape

        self._array: Optional[np.ndarray] = None
        self._shape = shape
        self._numbytes = 0

        # TODO: Implement a method to initialized 'self._array' ???

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        return f"{cls_name}<shape={self.shape}, dtype={self.dtype}>"

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self.shape == other.shape
        # if self.has_array: .... implement
        # return type(self) is type(other) and np.array_equal(self.array, other.array)

    def validate_type(self, value: np.ndarray) -> None:
        """Validate a value.

        Parameters
        ----------
        value
        """
        cls_name: str = self.__class__.__name__

        if not isinstance(value, np.ndarray):
            raise TypeError(f"{cls_name} array should be a numpy.ndarray")

        if value.dtype not in self.TYPE_LIST:
            exp_type_name: str = str(self.EXP_TYPE)
            raise TypeError(f"Expected type of {cls_name} array is {exp_type_name}.")

    def validate_shape(self, value: np.ndarray) -> None:
        """TBW."""
        cls_name: str = self.__class__.__name__

        if value.shape != self._shape:
            raise ValueError(f"Expected {cls_name} array is {self._array.shape}.")

    def __array__(self, dtype: Optional[np.dtype] = None):
        if not isinstance(self._array, np.ndarray):
            raise TypeError("Array not initialized.")
        return np.asarray(self._array, dtype=dtype)

    @property
    def has_array(self) -> bool:
        """Returns true if the array is initialized."""
        return self._array is not None

    def copy_array(self, auto_create: bool = False) -> Optional[np.ndarray]:
        """Returns true if the array is initialized."""
        if self._array is None and auto_create:
            self._array = np.zeros(shape=self._shape, dtype=self.dtype)
        if self._array is not None:
            return self._array.copy()
        return None

    @property
    def shape(self) -> tuple[int, int]:
        """Return array shape."""
        num_cols, num_rows = self._shape
        return num_cols, num_rows

    @property
    def ndim(self) -> int:
        """Return number of dimensions of the array."""
        return len(self._shape)

    @property
    def dtype(self) -> np.dtype:
        """Return array data type."""
        if self._array:
            return self._array.dtype
        return self.EXP_TYPE

    @property
    def array(self) -> np.ndarray:
        """Two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.
        """
        if self._array is None:
            raise ValueError("'array' is not initialized.")
        return self._array

    @array.setter
    def array(self, value: np.ndarray) -> None:
        """Overwrite the two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.
        """
        self.validate_type(value)
        self.validate_shape(value)

        self._array = value

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

    def to_xarray(self, dtype: Optional[np.typing.DTypeLike] = None) -> "xr.DataArray":
        """Convert into a 2D `DataArray` object with dimensions 'y' and 'x'.

        Parameters
        ----------
        dtype : data-type, optional
            Force a data-type for the array.

        Returns
        -------
        DataArray
            2D DataArray objects.

        Examples
        --------
        >>> detector.photon.to_xarray(dtype=float)
        <xarray.DataArray 'photon' (y: 100, x: 100)>
        array([[15149., 15921., 15446., ..., 15446., 15446., 16634.],
               [15149., 15446., 15446., ..., 15921., 16396., 17821.],
               [14555., 14971., 15446., ..., 16099., 16337., 17168.],
               ...,
               [16394., 16334., 16334., ..., 16562., 16325., 16325.],
               [16334., 15978., 16215., ..., 16444., 16444., 16206.],
               [16097., 15978., 16215., ..., 16681., 16206., 16206.]])
        Coordinates:
          * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
          * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        Attributes:
            units:      Ph
        """
        import xarray as xr

        num_rows, num_cols = self.shape
        if not self.has_array:
            return xr.DataArray()

        return xr.DataArray(
            np.array(self.array, dtype=dtype),
            name=self.NAME.lower(),
            dims=["y", "x"],
            coords={"y": range(num_rows), "x": range(num_cols)},
            attrs={"units": convert_unit(self.UNIT), "long_name": self.NAME},
        )

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
        import matplotlib.pyplot as plt

        arr: xr.DataArray = self.to_xarray()

        arr.plot(robust=robust)
        plt.title(self.NAME)
