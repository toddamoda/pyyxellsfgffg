"""TBW."""
import logging
import typing as t  # noqa: F401
from collections import OrderedDict

import esapy_config as om

from pyxel.detectors.detector import Detector
# from pyxel.pipelines.models import Model  # noqa: F401
from pyxel.pipelines.models import Models
from pyxel import util
# from pyxel.util import objmod as om


class DetectionPipeline:
    """TBW."""

    def __init__(self,
                 photon_generation: Models = None,
                 optics: Models = None,
                 charge_generation: Models = None,
                 charge_collection: Models = None,
                 charge_measurement: Models = None,
                 readout_electronics: Models = None,
                 doc=None) -> None:
        """TBW.

        :param optics:
        :param charge_generation:
        :param charge_collection:
        :param charge_measurement:
        :param readout_electronics:
        :param doc:
        """
        self._is_running = False
        self.doc = doc
        self.photon_generation = photon_generation
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_measurement = charge_measurement
        self.readout_electronics = readout_electronics

        self._name = ''
        self._model_groups = []  # type: t.List[str]
        self._model_steps = {}   # type: t.Dict[str, t.List[str]]
        self._log = logging.getLogger(__name__)

    @property
    def name(self):
        """TBW."""
        return self._name

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        def state(ref):
            """TBW."""
            if ref:
                return ref  # .__getstate__()

        return {
            'photon_generation': self.photon_generation,
            'optics': self.optics,
            'charge_generation': self.charge_generation,
            'charge_collection': self.charge_collection,
            'charge_measurement': self.charge_measurement,
            'readout_electronics': self.readout_electronics,
        }

    def clear(self):
        """Remove all the models from this pipeline."""
        for model_group in self.model_groups.values():
            if model_group.models:
                model_group.models.clear()

    def set_model_enabled(self, expression: str, is_enabled: bool):
        """TBW.

        :param expression:
        :param is_enabled:
        :return:
        """
        groups = self.model_groups
        for group_name, group in groups.items():
            for model in group.models:
                model_name = model.name
                can_set = 0
                can_set |= expression == '*'
                can_set |= group_name in expression
                can_set |= model_name in expression
                if can_set:
                    model.enabled = is_enabled

    @property
    def model_groups(self):
        """TBW."""
        result = OrderedDict()
        for group in self._model_groups:
            model_group = getattr(self, group)
            if model_group:
                result[group] = model_group
        return result

    @property
    def model_group_names(self):
        """TBW."""
        return self._model_groups

    def run(self, detector: Detector) -> Detector:
        """TBW."""
        try:
            self._is_running = True
            return self.run_pipeline(detector)
        except util.PipelineAborted:
            raise  # send signal to caller to ensure no output is saved
        finally:
            self._is_running = False

    def abort(self):
        """TBW."""
        self._is_running = False

    @property
    def is_running(self):
        """Return the running state of this pipeline."""
        return self._is_running

    def get_model(self, name):
        """TBW.

        :param name:
        :return:
        """
        for group in self._model_groups:
            steps = self._model_steps[group]
            if name in steps:
                models_obj = getattr(self, group)  # type: Models
                if models_obj:
                    if name in models_obj.models:
                        return models_obj.models[name]

    def run_model_group(self, name, detector):
        """TBW.

        :param name:
        :param detector:
        :return:
        """
        self._is_running = True
        if name in self._model_groups:
            models_obj = getattr(self, name)
            if models_obj:
                models_obj.run(detector, self)
        return detector

    def run_pipeline(self, detector: Detector) -> Detector:
        """TBW.

        :param detector:
        :return:
        """
        raise NotImplementedError
