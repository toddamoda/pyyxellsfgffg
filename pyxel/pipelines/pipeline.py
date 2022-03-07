#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import typing as t

from pyxel.pipelines import ModelFunction, ModelGroup


class DetectionPipeline:
    """TBW."""

    # TODO: develop a ModelGroupList class ? See #333
    def __init__(
        self,  # TODO: Too many instance attributes
        photon_generation: t.Optional[t.Sequence[ModelFunction]] = None,
        optics: t.Optional[t.Sequence[ModelFunction]] = None,
        phasing: t.Optional[t.Sequence[ModelFunction]] = None,
        charge_generation: t.Optional[t.Sequence[ModelFunction]] = None,
        charge_collection: t.Optional[t.Sequence[ModelFunction]] = None,
        charge_transfer: t.Optional[t.Sequence[ModelFunction]] = None,
        charge_measurement: t.Optional[t.Sequence[ModelFunction]] = None,
        signal_transfer: t.Optional[t.Sequence[ModelFunction]] = None,
        readout_electronics: t.Optional[t.Sequence[ModelFunction]] = None,
        doc: t.Optional[str] = None,
    ):
        self._is_running = False
        self.doc = doc

        self._photon_generation = (
            ModelGroup(photon_generation, name="photon_generation")
            if photon_generation
            else None
        )  # type: t.Optional[ModelGroup]

        self._optics = (
            ModelGroup(optics, name="optics") if optics else None
        )  # type: t.Optional[ModelGroup]

        self._phasing = (
            ModelGroup(phasing, name="phasing") if phasing else None
        )  # type: t.Optional[ModelGroup] # MKID-array

        self._charge_generation = (
            ModelGroup(charge_generation, name="charge_generation")
            if charge_generation
            else None
        )  # type: t.Optional[ModelGroup]

        self._charge_collection = (
            ModelGroup(charge_collection, name="charge_collection")
            if charge_collection
            else None
        )  # type: t.Optional[ModelGroup]

        self._charge_measurement = (
            ModelGroup(charge_measurement, name="charge_measurement")
            if charge_measurement
            else None
        )  # type: t.Optional[ModelGroup]

        self._readout_electronics = (
            ModelGroup(readout_electronics, name="readout_electronics")
            if readout_electronics
            else None
        )  # type: t.Optional[ModelGroup]

        self._charge_transfer = (
            ModelGroup(charge_transfer, name="charge_transfer")
            if charge_transfer
            else None
        )  # type: t.Optional[ModelGroup]  # CCD

        self._signal_transfer = (
            ModelGroup(signal_transfer, name="signal_transfer")
            if signal_transfer
            else None
        )  # type: t.Optional[ModelGroup]  # CMOS

        # TODO: this defines the order of steps in the pipeline.
        #       The ModelGroupList could do this. Is it really needed?
        self.MODEL_GROUPS = (
            "photon_generation",
            "optics",
            "phasing",
            "charge_generation",
            "charge_collection",
            "charge_transfer",
            "charge_measurement",
            "signal_transfer",
            "readout_electronics",
        )  # type: t.Tuple[str, ...]

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<is_running={self._is_running!r}, doc={self.doc!r}>"

    def __iter__(self) -> t.Iterable[ModelFunction]:
        for model in self.MODEL_GROUPS:
            models_grp = getattr(self, model)  # type: t.Optional[ModelGroup]
            if models_grp:
                yield from models_grp

    @property
    def photon_generation(self) -> t.Optional[ModelGroup]:
        """Get group 'photon generation'."""
        return self._photon_generation

    @property
    def optics(self) -> t.Optional[ModelGroup]:
        """Get group 'optics'."""
        return self._optics

    @property
    def phasing(self) -> t.Optional[ModelGroup]:
        """Get group 'phasing'."""
        return self._phasing

    @property
    def charge_generation(self) -> t.Optional[ModelGroup]:
        """Get group 'charge generation'."""
        return self._charge_generation

    @property
    def charge_collection(self) -> t.Optional[ModelGroup]:
        """Get group 'charge collection'."""
        return self._charge_collection

    @property
    def charge_transfer(self) -> t.Optional[ModelGroup]:
        """Get group 'charge transfer'."""
        return self._charge_transfer

    @property
    def charge_measurement(self) -> t.Optional[ModelGroup]:
        """Get group 'charge measurement'."""
        return self._charge_measurement

    @property
    def signal_transfer(self) -> t.Optional[ModelGroup]:
        """Get group 'signal transfer'."""
        return self._signal_transfer

    @property
    def readout_electronics(self) -> t.Optional[ModelGroup]:
        """Get group 'readout electronics'."""
        return self._readout_electronics

    @property
    def model_group_names(self) -> t.Tuple[str, ...]:
        """TBW."""
        return self.MODEL_GROUPS

    @property
    def is_running(self) -> bool:
        """Return the running state of this pipeline."""
        return self._is_running

    def abort(self) -> None:
        """TBW."""
        self._is_running = False

    # TODO: Is this method used ?
    def get_model(self, name: str) -> ModelFunction:
        """Return a ModelFunction object for the specified model name.

        Parameters
        ----------
        name: str
            Name of the model.

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            If model with the specified name is not found.
        """
        for group_name in self.model_group_names:  # type: str
            model_group = getattr(self, group_name)  # type: ModelGroup
            if model_group:
                for model in model_group.models:  # type: ModelFunction
                    if name == model.name:
                        return model
        raise AttributeError("Model has not been found.")
