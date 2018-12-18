"""TBW."""
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_group import ModelGroup


class CCDDetectionPipeline(DetectionPipeline):
    """TBW."""

    def __init__(self,
                 charge_transfer: ModelGroup = None,
                 **kwargs) -> None:
        """TBW.

        :param charge_transfer:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.charge_transfer = charge_transfer

        self._model_groups = ['photon_generation',                  # TODO
                              'optics',
                              'charge_generation',
                              'charge_collection',
                              'charge_transfer',
                              'charge_measurement',
                              'readout_electronics']

    def __getstate__(self):
        """TBW."""
        kwargs = super().__getstate__()
        kwargs_obj = {
            'charge_transfer': self.charge_transfer,
            '_model_groups': self._model_groups,             # TODO
        }
        return {**kwargs, **kwargs_obj}

    def run_pipeline(self, detector: Detector) -> Detector:
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
