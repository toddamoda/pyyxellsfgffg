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

            # TODO: Refactor
            if with_intermediate_steps:
                import xarray as xr
                from datatree import DataTree

                # Get current absolute time
                absolute_time = xr.DataArray(
                    [detector.absolute_time],
                    dims=["time"],
                    attrs={"units": "s"},
                )

                # Get current Dataset
                absolute_time = xr.DataArray(absolute_time, attrs={"units": "s"})
                ds: xr.Dataset = detector.to_xarray().assign_coords(time=absolute_time)

                # Get datatree parent 'intermediate'
                intermediate_key: str = "intermediate"
                if intermediate_key not in detector.data:
                    datatree_intermediate: DataTree = DataTree(
                        name="intermediate", parent=detector.data
                    )
                    datatree_intermediate.attrs = {
                        "long_name": (
                            "Store all intermediate results modified along a pipeline"
                        )
                    }
                else:
                    datatree_intermediate = detector.data[intermediate_key]  # type: ignore

                # TODO: Refactor
                pipeline_key: str = f"idx_{detector.pipeline_count}"
                if pipeline_key not in datatree_intermediate:
                    datatree_one_time: DataTree = DataTree(
                        name=pipeline_key, parent=datatree_intermediate
                    )
                    datatree_one_time.attrs = {
                        "long_name": "Pipeline for one unique time",
                        "pipeline_count": detector.pipeline_count,
                        "time": f"{detector.absolute_time} s",
                    }
                else:
                    datatree_one_time = datatree_intermediate[pipeline_key]  # type: ignore

                # TODO: Refactor
                model_group_key: str = self._name
                if model_group_key not in datatree_one_time:
                    datatree_group: DataTree = DataTree(
                        name=model_group_key, parent=datatree_one_time
                    )
                    datatree_group.attrs = {"long_name": f"Model group: {self._name!r}"}
                else:
                    datatree_group = datatree_one_time[model_group_key]  # type: ignore

                # TODO: Refactor
                model_key: str = model.name
                if model_key not in datatree_group:
                    datatree_model: DataTree = DataTree(
                        name=model_key, parent=datatree_group
                    )
                    datatree_model.attrs = {"long_name": f"Group: {model.name!r}"}
                else:
                    datatree_model = datatree_group[model_key]  # type: ignore

                # TODO: Refactor
                last_key: str = "last"
                if last_key not in datatree_intermediate:
                    last_full_ds: xr.Dataset = xr.zeros_like(ds)
                else:
                    last_full_ds = datatree_intermediate[last_key]  # type: ignore

                for name, data_array in ds.data_vars.items():
                    previous_data_array = last_full_ds[name]

                    if not data_array.equals(previous_data_array):
                        datatree_model[name] = data_array

                # datatree_model
                datatree_intermediate[last_key] = DataTree(ds.copy(deep=True))
