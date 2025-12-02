#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

""":term:`CMOS` detector modeling class."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import numpy as np

from pyxel.data_structure import _get_array_if_initialized
from pyxel.detectors import Detector
from pyxel.util import PinkNoiseGenerator, set_random_seed

if TYPE_CHECKING:
    import pandas as pd

    from pyxel.detectors import Characteristics, CMOSGeometry, Environment


class CMOS(Detector):
    """:term:`CMOS`-based detector class containing all detector attributes and data."""

    def __init__(
        self,
        geometry: "CMOSGeometry",
        environment: "Environment",
        characteristics: "Characteristics",
    ):
        self._geometry: CMOSGeometry = geometry

        self._characteristics: Characteristics = characteristics
        self._characteristics.initialize(self._geometry)

        self._uncorrelated_pink_noise_generators: (
            dict[str, PinkNoiseGenerator] | None
        ) = None

        super().__init__(environment=environment)
        super()._initialize()

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self.geometry == other.geometry
            and self.environment == other.environment
            and self.characteristics == other.characteristics
            and super().__eq__(other)
        )

    @property
    def geometry(self) -> "CMOSGeometry":
        return self._geometry

    @property
    def characteristics(self) -> "Characteristics":
        return self._characteristics

    @property
    def uncorrelated_pink_noise_generators(self) -> dict[str, PinkNoiseGenerator]:
        if self._uncorrelated_pink_noise_generators is None:
            raise RuntimeError("'uncorrelated_pink_noise_generators' not initialized.")
        else:
            return self._uncorrelated_pink_noise_generators

    def set_uncorrelated_pink_noise_generators(self, seed: int | None = None) -> None:
        if self.geometry.channels:
            chan_labels = list(self.geometry.channels)
        else:
            chan_labels = ["default"]
        self._uncorrelated_pink_noise_generators = dict()
        # we use the given seed to provide a different seed to each channel
        with set_random_seed(seed):
            for chan_label in chan_labels:
                sd = np.random.randint(10_000)
                self._uncorrelated_pink_noise_generators[chan_label] = (
                    PinkNoiseGenerator(sd)
                )

    # TODO: refactor to split up to empty and reset.
    def empty(self, reset: bool = True) -> None:
        super().empty(reset)
        if reset:
            # pixel.non_volatile is emptied when `reset` is `True`,
            # so it seems noise generator should be nullified too
            self._uncorrelated_pink_noise_generators = None

    # TODO: Refactor this
    def to_dict(self) -> Mapping:
        """Convert an instance of `CMOS` to a `dict`."""
        dct = {
            "version": 1,
            "type": "CMOS",
            "properties": {
                "geometry": self.geometry.to_dict(),
                "environment": self.environment.to_dict(),
                "characteristics": self.characteristics.to_dict(),
            },
            "data": {
                "photon": self.photon.to_dict(),
                "pixel": self._pixel.to_dict() if self._pixel else None,
                "signal": _get_array_if_initialized(self._signal),
                "image": _get_array_if_initialized(self._image),
                "data": (
                    None
                    if self._data is None
                    else {
                        key.replace("/", "#"): value
                        for key, value in self._data.to_dict().items()
                    }
                ),
                "charge": (
                    None
                    if self._charge is None
                    else {
                        "array": self._charge.array.copy(),
                        "frame": self._charge.frame.copy(),
                    }
                ),
                "scene": (
                    None
                    if self._scene is None
                    else {
                        key.replace("/", "#"): value
                        for key, value in self._scene.to_dict().items()
                    }
                ),
            },
        }

        return dct

    # TODO: Refactor this
    @classmethod
    def from_dict(cls, dct: Mapping) -> "CMOS":
        """Create a new instance of `CMOS` from a `dict`."""
        # TODO: This is a simplistic implementation. Improve this.
        import numpy as np
        import xarray as xr

        from pyxel.data_structure import Photon, Pixel, Scene
        from pyxel.detectors import Characteristics, CMOSGeometry, Environment

        if dct["type"] != "CMOS":
            raise ValueError

        if dct["version"] != 1:
            raise ValueError

        properties = dct["properties"]
        geometry = CMOSGeometry.from_dict(properties["geometry"])
        environment = Environment.from_dict(properties["environment"])
        characteristics = Characteristics.from_dict(properties["characteristics"])

        detector = cls(
            geometry=geometry,
            environment=environment,
            characteristics=characteristics,
        )

        data: Mapping[str, Any] = dct["data"]

        detector.photon = Photon.from_dict(
            geometry=geometry, data=data.get("photon", dict())
        )
        detector.pixel = Pixel.from_dict(
            geometry=geometry, data=data.get("pixel", dict())
        )
        detector.signal.update(data.get("signal"))
        detector.image.update(data.get("image"))

        if "data" in data:
            detector._data = xr.DataTree.from_dict(
                {
                    key.replace("#", "/"): xr.Dataset.from_dict(value)
                    for key, value in data["data"].items()
                }
            )
        if "scene" in data and (scene_dct := data["scene"]) is not None:
            detector.scene = Scene.from_dict(
                {key.replace("#", "/"): value for key, value in scene_dct.items()}
            )
        if "charge" in data and data["charge"] is not None:
            charge_dct = data["charge"]
            detector.charge._array = np.asarray(charge_dct["array"])

            new_frame: pd.DataFrame = charge_dct["frame"]
            previous_frame: pd.DataFrame = detector.charge._frame
            detector.charge._frame = new_frame[previous_frame.columns]

        return detector
