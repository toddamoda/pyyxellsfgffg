"""TBW."""
import logging
import typing as t  # noqa: F401

from pyxel.detectors.detector import Detector
from pyxel.pipelines.models import Model  # noqa: F401
from pyxel.pipelines.models import Models
from pyxel import util


class PipelineAborted(Exception):
    """Exception to force the pipeline to stop processing."""


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
        self._is_running = False
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

    def get_state_json(self):
        """TBW."""
        return util.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        def state(ref):
            """TBW."""
            if ref:
                return ref  # .__getstate__()

        return {
            'photon_generation': state(self.photon_generation),
            'optics': state(self.optics),
            'charge_generation': state(self.charge_generation),
            'charge_collection': state(self.charge_collection),
            'charge_measurement': state(self.charge_measurement),
            'readout_electronics': state(self.readout_electronics),
        }

    @property
    def model_groups(self):
        """TBW."""
        return self._model_groups

    def run(self, detector: Detector) -> Detector:
        """TBW."""
        try:
            self._is_running = True
            return self.run_pipeline(detector)
        except PipelineAborted:
            raise  # send signal to caller to ensure no output is saved
        finally:
            self._is_running = False

    def abort(self):
        """TBW."""
        self._is_running = False

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
            steps = self._model_steps[name]
            models_obj = getattr(self, name)  # type: Models
            if models_obj:
                for step in steps:
                    if step in models_obj.models:
                        model = models_obj.models[step]  # type: Model
                        if model.enabled:
                            self._log.debug('Running %r', model.name)
                            for arg in model.arguments:
                                util.update_fits_header(detector.header,
                                                        key=[step, arg],
                                                        value=model.arguments[arg])
                            model.function(detector)
                            if not self._is_running:
                                self._log.debug('Aborted after %r', model.name)
                                raise PipelineAborted()
                        else:
                            self._log.debug('Skipping %r', model.name)
        return detector

    def run_pipeline(self, detector: Detector) -> Detector:
        """TBW.

        :param detector:
        :return:
        """
        raise NotImplementedError
