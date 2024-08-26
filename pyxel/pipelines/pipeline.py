#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

from collections.abc import Iterator, Sequence
from typing import Optional

from pyxel.pipelines import ModelFunction, ModelGroup


class DetectionPipeline:
    """Represent a pipeline of detection models organized into different groups."""

    # Define the order of steps in the pipeline.
    MODEL_GROUPS: tuple[str, ...] = (
        "scene_generation",
        "photon_collection",
        "phasing",
        "charge_generation",
        "charge_collection",
        "charge_transfer",
        "charge_measurement",
        "signal_transfer",
        "readout_electronics",
        "data_processing",
    )

    # TODO: develop a ModelGroupList class ? See #333
    def __init__(
        self,  # TODO: Too many instance attributes
        scene_generation: Optional[Sequence[ModelFunction]] = None,
        photon_collection: Optional[Sequence[ModelFunction]] = None,
        phasing: Optional[Sequence[ModelFunction]] = None,
        charge_generation: Optional[Sequence[ModelFunction]] = None,
        charge_collection: Optional[Sequence[ModelFunction]] = None,
        charge_transfer: Optional[Sequence[ModelFunction]] = None,
        charge_measurement: Optional[Sequence[ModelFunction]] = None,
        signal_transfer: Optional[Sequence[ModelFunction]] = None,
        readout_electronics: Optional[Sequence[ModelFunction]] = None,
        data_processing: Optional[Sequence[ModelFunction]] = None,
    ):
        self._scene_generation: Optional[ModelGroup] = (
            ModelGroup(scene_generation, name="scene_generation")
            if scene_generation
            else None
        )

        self._photon_collection: Optional[ModelGroup] = (
            ModelGroup(photon_collection, name="photon_collection")
            if photon_collection
            else None
        )

        self._phasing: Optional[ModelGroup] = (
            ModelGroup(phasing, name="phasing") if phasing else None
        )  # MKID-array

        self._charge_generation: Optional[ModelGroup] = (
            ModelGroup(charge_generation, name="charge_generation")
            if charge_generation
            else None
        )

        self._charge_collection: Optional[ModelGroup] = (
            ModelGroup(charge_collection, name="charge_collection")
            if charge_collection
            else None
        )

        self._charge_measurement: Optional[ModelGroup] = (
            ModelGroup(charge_measurement, name="charge_measurement")
            if charge_measurement
            else None
        )

        self._readout_electronics: Optional[ModelGroup] = (
            ModelGroup(readout_electronics, name="readout_electronics")
            if readout_electronics
            else None
        )

        self._charge_transfer: Optional[ModelGroup] = (
            ModelGroup(charge_transfer, name="charge_transfer")
            if charge_transfer
            else None
        )  # CCD

        self._signal_transfer: Optional[ModelGroup] = (
            ModelGroup(signal_transfer, name="signal_transfer")
            if signal_transfer
            else None
        )  # CMOS

        self._data_processing: Optional[ModelGroup] = (
            ModelGroup(data_processing, name="data_processing")
            if data_processing
            else None
        )

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__

        return f"{cls_name}<{len(list(self))} model(s)>"

    def __iter__(self) -> Iterator[ModelFunction]:
        for model in self.MODEL_GROUPS:
            models_grp: Optional[ModelGroup] = getattr(self, model)
            if models_grp:
                yield from models_grp

    @property
    def scene_generation(self) -> Optional[ModelGroup]:
        """Get group 'scene generation'."""
        return self._scene_generation

    @property
    def photon_collection(self) -> Optional[ModelGroup]:
        """Get group 'photon collection'."""
        return self._photon_collection

    @property
    def phasing(self) -> Optional[ModelGroup]:
        """Get group 'phasing'."""
        return self._phasing

    @property
    def charge_generation(self) -> Optional[ModelGroup]:
        """Get group 'charge generation'."""
        return self._charge_generation

    @property
    def charge_collection(self) -> Optional[ModelGroup]:
        """Get group 'charge collection'."""
        return self._charge_collection

    @property
    def charge_transfer(self) -> Optional[ModelGroup]:
        """Get group 'charge transfer'."""
        return self._charge_transfer

    @property
    def charge_measurement(self) -> Optional[ModelGroup]:
        """Get group 'charge measurement'."""
        return self._charge_measurement

    @property
    def signal_transfer(self) -> Optional[ModelGroup]:
        """Get group 'signal transfer'."""
        return self._signal_transfer

    @property
    def readout_electronics(self) -> Optional[ModelGroup]:
        """Get group 'readout electronics'."""
        return self._readout_electronics

    @property
    def data_processing(self) -> Optional[ModelGroup]:
        """Get group 'data processing'."""
        return self._data_processing

    @property
    def model_group_names(self) -> tuple[str, ...]:
        """Get all model groups."""
        return self.MODEL_GROUPS

    # TODO: Is this method used ?
    def get_model(self, name: str) -> ModelFunction:
        """Return a ``ModelFunction`` object for the specified model name.

        Parameters
        ----------
        name: str
            Name of the model.

        Returns
        -------
        ModelFunction

        Raises
        ------
        AttributeError
            If model with the specified name is not found.
        """
        group_name: str
        for group_name in self.model_group_names:
            model_group: ModelGroup = getattr(self, group_name)
            if model_group:
                model: ModelFunction
                for model in model_group.models:
                    if name == model.name:
                        return model
        raise AttributeError("Model has not been found.")

    def describe(self) -> Iterator[str]:
        for model_group_name in self.MODEL_GROUPS:
            models_grp: Optional[ModelGroup] = getattr(self, model_group_name)
            if not models_grp:
                continue

            yield f"Group: {models_grp._name}"

            model: ModelFunction
            for model in models_grp:
                yield f"  Func: {model.func.__module__}.{model.func.__name__}"
                yield f"  name: {model.name}"

                for key, value in model.arguments.items():
                    yield f"    {key}: {value}"
