"""TBW."""
import logging
import typing as t  # noqa: F401

from pyxel.detectors.detector import Detector
from pyxel.pipelines.models import Models
from pyxel.pipelines.models import Model


class DetectionPipeline:
    """TBW."""

    def __init__(self,
                 photon_generation: Models,
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
        self.photon_generation = photon_generation
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_measurement = charge_measurement
        self.readout_electronics = readout_electronics

        self._model_groups = []  # type: t.List[str]
        self._model_steps = {}   # type: t.Dict[str, t.List[str]]
        self._log = logging.getLogger(__name__)

    def run_model_group(self, name, detector):
        """TBW.

        :param name:
        :param detector:
        :return:
        """
        if name in self._model_groups:
            steps = self._model_steps[name]
            models_obj = getattr(self, name)  # type: Models
            if models_obj:
                for step in steps:
                    if step in models_obj.models:
                        model = models_obj.models[step]  # type: Model
                        if model.enabled:
                            self._log.debug('Running %r', model.name)
                            model.function(detector)
                        else:
                            self._log.debug('Skipping %r', model.name)
        return detector

    def run_pipeline(self, detector: Detector) -> Detector:
        """TBW.

        :param detector:
        :return:
        """
        raise NotImplementedError
