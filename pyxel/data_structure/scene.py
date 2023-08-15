#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Scene class to track multi-wavelength photon."""

from collections.abc import Mapping
from typing import TYPE_CHECKING

import xarray as xr
from datatree import DataTree

if TYPE_CHECKING:
    from scopesim import Source


class Scene:
    """Scene class defining and storing information of all multi-wavelength photon."""

    def __init__(self):
        self._source: DataTree = DataTree(name="scene")

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self.data.identical(other.data)

    def add_source(self, source: xr.Dataset) -> None:
        """Add a source to the current scene.

        Parameters
        ----------
        source : Dataset

        Raises
        ------
        TypeError
            If 'source' is not a ``Dataset`` object.
        ValueError
            If 'source' has not the expected format.

        Examples
        --------
        >>> from pyxel.detectors import CCD
        >>> detector = CCD(...)
        >>> detector.reset()

        >>> source
        <xarray.Dataset>
        Dimensions:     (ref: 345, wavelength: 343)
        Coordinates:
          * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
          * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
        Data variables:
            x           (ref) float64 1.334e+03 1.434e+03 ... -1.271e+03 -1.381e+03
            y           (ref) float64 -1.009e+03 -956.1 -797.1 ... 1.195e+03 1.309e+03
            weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
            flux        (ref, wavelength) float64 0.003769 0.004137 ... 0.1813 0.1896

        >>> detector.scene.add_source(source)
        >>> detector.scene.data
        DataTree('scene', parent=None)
        └── DataTree('list')
            └── DataTree('0')
                    Dimensions:     (ref: 4, wavelength: 4)
                    Coordinates:
                      * ref         (ref) int64 0 1 2 3
                      * wavelength  (wavelength) float64 336.0 338.0 1.018e+03 1.02e+03
                    Data variables:
                        x           (ref) float64 64.97 11.44 -55.75 -20.66
                        y           (ref) float64 89.62 -129.3 -48.16 87.87
                        weight      (ref) float64 14.73 12.34 14.63 14.27
                        flux        (ref, wavelength) float64 0.003769 0.004137 ... 0.1813 0.1896
        """
        if not isinstance(source, xr.Dataset):
            raise TypeError("Expecting a Dataset object for source")

        if set(source.coords) != {"ref", "wavelength"}:
            raise ValueError(
                "Wrong format for source. Expecting coordinates 'ref' and 'wavelength'."
            )

        if set(source.data_vars) != {
            "x",
            "y",
            "weight",
            "flux",
        }:
            raise ValueError(
                "Wrong format for source. Expecting a Dataset with variables 'x', 'y', 'weight' and 'flux'."
            )

        if "list" not in self.data:
            key: int = 0
        else:
            key = self.data.width

        self.data[f"/list/{key}"] = DataTree(source)

    # TODO: This method will be removed in the future.
    #       If you want to have a `Source` object, you should use method '.to_scopesim'
    @property
    def data(self) -> DataTree:
        """Get a multi-wavelength object."""
        return self._source

    def from_scopesim(self, source: "Source") -> None:
        """Convert a ScopeSim `Source` object into a `Scene` object.

        Parameters
        ----------
        source : scopesim.Source
            Object to convert to a `Scene` object.

        Raises
        ------
        RuntimeError
            If package 'scopesim' is not installed.
        TypeError
            If input parameter 'source' is not a ScopeSim `Source` object.

        Notes
        -----
        More information about ScopeSim `Source` objects at
        this link: https://scopesim.readthedocs.io/en/latest/reference/scopesim.source.source.html
        """
        try:
            from scopesim import Source
        except ImportError as exc:
            raise RuntimeError(
                "Package 'scopesim' is not installed ! "
                "Please run command 'pip install scopesim' from the command line."
            ) from exc

        if not isinstance(source, Source):
            raise TypeError("Expecting a ScopeSim `Source` object for 'source'.")

        raise NotImplementedError

    def to_scopesim(self) -> "Source":
        """Convert this `Scene` object into a ScopeSim `Source` object.

        Returns
        -------
        Source
            A ScopeSim `Source` object.

        Notes
        -----
        More information about ScopeSim `Source` objects at
        this link: https://scopesim.readthedocs.io/en/latest/reference/scopesim.source.source.html
        """
        raise NotImplementedError

    def to_dict(self) -> Mapping:
        """Convert an instance of `Scene` to a `dict`."""
        result: Mapping = {
            key: value.to_dict() for key, value in self.data.to_dict().items()
        }

        return result

    @classmethod
    def from_dict(cls, dct: Mapping) -> "Scene":
        """Create a new instance of a `Scene` object from a `dict`."""
        data: Mapping[str, xr.Dataset] = {
            key: xr.Dataset.from_dict(value) for key, value in dct.items()
        }

        scene = cls()
        scene._source = DataTree.from_dict(data, name="scene")  # type: ignore

        return scene
