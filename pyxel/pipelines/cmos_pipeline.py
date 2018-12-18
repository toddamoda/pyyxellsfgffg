"""TBW."""
# from pyxel import util
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_group import ModelGroup


class CMOSDetectionPipeline(DetectionPipeline):
    """TBW."""

    def __init__(self,
                 signal_transfer: ModelGroup = None,
                 **kwargs) -> None:
        """TBW.

        :param signal_transfer:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.signal_transfer = signal_transfer

        # self._name = 'cmos'
        self._model_groups = ['photon_generation',
                              'optics',
                              'charge_generation',
                              'charge_collection',
                              'charge_measurement',
                              'signal_transfer',
                              'readout_electronics']

    def __getstate__(self):
        """TBW."""
        kwargs = super().__getstate__()
        kwargs_obj = {
            'signal_transfer': self.signal_transfer,
            # '_name': self._name,
            '_model_groups': self.model_group_names,
            # '_model_steps': self._model_steps
        }
        return {**kwargs, **kwargs_obj}

    # def run_pipeline(self, detector: Detector) -> Detector:
    #     """TBW."""
    #     # INITIALIZATION (open or generate image):
    #     # START -> create photons ->
    #     detector = self.run_model_group('photon_generation', detector)
    #
    #     # OPTICS:
    #     # -> transport/modify photons ->
    #     detector = self.run_model_group('optics', detector)
    #
    #     # CHARGE GENERATION:
    #     # -> create charges & remove photons ->
    #     detector = self.run_model_group('charge_generation', detector)
    #
    #     # CHARGE COLLECTION:
    #     # -> transport/modify charges ->
    #     # -> collect charges in pixels ->
    #     detector = self.run_model_group('charge_collection', detector)
    #
    #     # CHARGE READOUT
    #     # -> create signal ->
    #     detector = self.run_model_group('charge_measurement', detector)
    #
    #     # SIGNAL TRANSFER
    #     # -> modify signal ->
    #     detector = self.run_model_group('signal_transfer', detector)
    #
    #     # READOUT ELECTRONICS
    #     # -> create image -> modify image -> END
    #     detector = self.run_model_group('readout_electronics', detector)
    #
    #     return detector
