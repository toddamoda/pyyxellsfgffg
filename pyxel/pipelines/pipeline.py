"""TBW."""
# import logging
import typing as t  # noqa: F401
from pyxel.pipelines.model_group import ModelGroup
from pyxel.detectors.detector import Detector


class DetectionPipeline:
    """TBW."""

    def __init__(self,      # TODO: Too many instance attributes
                 photon_generation: ModelGroup = None,
                 optics: ModelGroup = None,
                 charge_generation: ModelGroup = None,
                 charge_collection: ModelGroup = None,
                 charge_measurement: ModelGroup = None,
                 readout_electronics: ModelGroup = None,
                 _model_groups: t.List[str] = None,                        # TODO
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
        self.photon_generation = photon_generation              # type: t.Optional[ModelGroup]
        self.optics = optics                                    # type: t.Optional[ModelGroup]
        self.charge_generation = charge_generation              # type: t.Optional[ModelGroup]
        self.charge_collection = charge_collection              # type: t.Optional[ModelGroup]
        self.charge_measurement = charge_measurement            # type: t.Optional[ModelGroup]
        self.readout_electronics = readout_electronics          # type: t.Optional[ModelGroup]

        self._model_groups = []                                 # type: t.List[str]           # TODO
        # self._log = logging.getLogger(__name__)

    def __getstate__(self):
        """TBW."""
        return {
            'photon_generation': self.photon_generation,
            'optics': self.optics,
            'charge_generation': self.charge_generation,
            'charge_collection': self.charge_collection,
            'charge_measurement': self.charge_measurement,
            'readout_electronics': self.readout_electronics,
        }

    @property
    def model_group_names(self):
        """TBW."""
        return self._model_groups

    @property
    def is_running(self):
        """Return the running state of this pipeline."""
        return self._is_running

    def abort(self):
        """TBW."""
        self._is_running = False

    def get_model(self, name):
        """TBW.

        :param name:
        :return:
        """
        for group_name in self.model_group_names:
            model_group = getattr(self, group_name)     # type: ModelGroup
            if model_group:
                for model in model_group.models:
                    if name == model.name:
                        return model
        raise AttributeError('Model has not found.')

    def run_pipeline(self, detector: Detector, abort_before: str = None) -> Detector:
        """TBW.

        :param detector:
        :param abort_before: str, model name, the pipeline should be aborted before this
        :return:
        """
        self._is_running = True
        for group_name in self.model_group_names:
            models_grp = getattr(self, group_name)      # type: ModelGroup
            if models_grp:
                abort_flag = models_grp.run(detector, self, abort_model=abort_before)
                if abort_flag:
                    break
        self._is_running = False
        return detector
