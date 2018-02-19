"""TBW."""

import typing as t

from pyxel.detectors.detector import Detector
from pyxel.pipelines.models import Models


class DetectionPipeline:
    """TBW."""

    def __init__(self,
                 optics: Models,
                 charge_generation: Models,
                 charge_collection: Models,
                 charge_measurement: Models,
                 readout_electronics: Models,
                 doc=None) -> None:
        """TBW.

        :param optics:
        :param charge_generation:
        :param charge_collection:
        :param charge_measurement:
        :param readout_electronics:
        :param doc:
        """
        self.doc = doc
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_measurement = charge_measurement
        self.readout_electronics = readout_electronics

        self._model_groups = []  # type: t.List[str]
        self._model_steps = {}   # type: t.Dict[str, t.List[str]]

    def run_model_group(self, name, detector):
        """TBW.

        :param name:
        :param detector:
        :return:
        """
        if name in self._model_groups:
            steps = self._model_steps[name]
            model = getattr(self, name)
            for step in steps:
                func = model.models.get(step)
                if func:
                    detector = func(detector)
        return detector

    def run_pipeline(self, detector: Detector) -> Detector:
        """TBW.

        :param detector:
        :return:
        """
        raise NotImplementedError
