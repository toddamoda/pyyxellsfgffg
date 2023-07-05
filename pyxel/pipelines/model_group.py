#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import logging
from collections.abc import Iterator, Mapping, Sequence
from copy import deepcopy
from typing import TYPE_CHECKING

from pyxel.pipelines import ModelFunction

if TYPE_CHECKING:
    from pyxel.detectors import Detector


# TODO: These methods could also be as a `abc.Sequence` with magical methods:
#       __getitem__, __iter__, __len__, __contains__, ...
#       See #181
class ModelGroup:
    """TBW."""

    def __init__(self, models: Sequence[ModelFunction], name: str):
        self._log = logging.getLogger(__name__)
        self._name = name
        self.models: Sequence[ModelFunction] = models

    def __repr__(self):
        cls_name: str = self.__class__.__name__

        all_models: list[str] = [model.name for model in self.models if model.name]

        return f"{cls_name}<name={self._name!r}, models={all_models!r}>"

    def __deepcopy__(self, memo: dict) -> "ModelGroup":
        copied_models = deepcopy(self.models)
        return ModelGroup(models=copied_models, name=self._name)

    def __iter__(self) -> Iterator[ModelFunction]:
        for model in self.models:
            if model.enabled:
                yield model

    def __getstate__(self) -> Mapping:
        return {"models": tuple(self.models), "name": self._name}

    def __setstate__(self, state: Mapping) -> None:
        self.models = list(state["models"])
        self._name = state["name"]

    def __getattr__(self, item: str) -> ModelFunction:
        for model in self.models:
            if model.name == item:
                return model
        else:
            raise AttributeError(f"Cannot find model {item!r}.")

    def __dir__(self):
        return dir(type(self)) + [model.name for model in self.models]

    def run(
        self,
        detector: "Detector",
        with_intermediate_steps: bool = False,
    ):
        """Execute each enabled model in this group.

        Parameters
        ----------
        detector : Detector
        with_intermediate_steps : bool
        """
        model: ModelFunction
        for model in self:
            self._log.info("Model: %r", model.name)
            model(detector)

            if with_intermediate_steps:
                import xarray as xr
                from datatree import DataTree

                # Get current absolute time
                absolute_time = xr.DataArray(
                    [detector.absolute_time],
                    dims=["time"],
                    attrs={"units": "s"},
                )

                key: str = f"/intermediate/{self._name}/{model.name}"
                ds: xr.Dataset = detector.to_xarray().expand_dims(time=absolute_time)

                if detector.is_first_readout:
                    new_data_tree: DataTree = DataTree(ds)
                else:
                    previous_data_tree: DataTree = detector.data[key]  # type: ignore

                    new_data_tree = previous_data_tree.combine_first(ds)

                detector.data[key] = new_data_tree
