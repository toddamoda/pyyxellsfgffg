"""TBW."""
import logging
import typing as t  # noqa: F401
# import collections

import esapy_config as om

from pyxel.pipelines.model_group import ModelGroup
from pyxel.detectors.detector import Detector


class DetectionPipeline:
    """TBW."""

    def __init__(self,
                 photon_generation: ModelGroup = None,
                 optics: ModelGroup = None,
                 charge_generation: ModelGroup = None,
                 charge_collection: ModelGroup = None,
                 charge_measurement: ModelGroup = None,
                 readout_electronics: ModelGroup = None,
                 _model_groups=None,                        # TODO
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

        self._model_groups = []  # type: t.List[str]
        self._log = logging.getLogger(__name__)

    # @property
    # def name(self):
    #     """TBW."""
    #     return self._name

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        # def state(ref):
        #     """TBW."""
        #     if ref:
        #         return ref  # .__getstate__()

        return {
            'photon_generation': self.photon_generation,
            'optics': self.optics,
            'charge_generation': self.charge_generation,
            'charge_collection': self.charge_collection,
            'charge_measurement': self.charge_measurement,
            'readout_electronics': self.readout_electronics,
        }

    # def clear(self):
    #     """Remove all the models from this pipeline."""
    #     for model_group in self.model_groups.values():
    #         if model_group.models:
    #             model_group.models.clear()
    #
    # def set_model_enabled(self, expression: str, is_enabled: bool):
    #     """TBW.
    #
    #     :param expression:
    #     :param is_enabled:
    #     :return:
    #     """
    #     groups = self.model_groups
    #     for group_name, group in groups.items():
    #         for model in group.models:
    #             model_name = model.name
    #             can_set = 0
    #             can_set |= expression == '*'
    #             can_set |= group_name in expression
    #             can_set |= model_name in expression
    #             if can_set:
    #                 model.enabled = is_enabled
    #
    # @property
    # def model_groups(self):
    #     """TBW."""
    #     result = collections.OrderedDict()
    #     for group in self._model_groups:
    #         model_group = getattr(self, group)
    #         if model_group:
    #             result[group] = model_group
    #     return result

    @property
    def model_group_names(self):
        """TBW."""
        return self._model_groups

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
        for group_name in self.model_group_names:
            model_group = getattr(self, group_name)  # type: Models
            if model_group:
                for model in model_group.models:
                    if name == model.name:
                        return model
        raise AttributeError('Model has not found')

    def run_model_group(self, name, detector):
        """TBW.

        :param name:
        :param detector:
        :return:
        """
        self._is_running = True
        if name in self.model_group_names:
            models_obj = getattr(self, name)
            if models_obj:
                models_obj.run(detector, self)
        return detector

    def run_pipeline(self, detector: Detector) -> Detector:              # TODO TODO TODO TODO (like run_model_group)
        """TBW.

        :param detector:
        :return:
        """
        # START -> create photons ->
        detector = self.run_model_group('photon_generation', detector)

        # OPTICS:
        # -> transport/modify photons ->
        detector = self.run_model_group('optics', detector)

        # CHARGE GENERATION:
        # -> create charges & remove photons ->
        detector = self.run_model_group('charge_generation', detector)

        # CHARGE COLLECTION:
        # -> transport/modify charges -> collect charges in pixels ->
        detector = self.run_model_group('charge_collection', detector)

        # CHARGE TRANSFER:
        # -> transport/modify pixels ->
        detector = self.run_model_group('charge_transfer', detector)

        # CHARGE READOUT
        # -> create signal -> modify signal ->
        detector = self.run_model_group('charge_measurement', detector)

        # READOUT ELECTRONICS
        # -> create image -> modify image -> END
        detector = self.run_model_group('readout_electronics', detector)

        return detector

    # def run(self, detector: Detector) -> Detector:
    #     """TBW."""
    #     try:
    #         self._is_running = True
    #         return self.run_pipeline(detector)
    #     except util.PipelineAborted:
    #         raise  # send signal to caller to ensure no output is saved
    #     finally:
    #         self._is_running = False
