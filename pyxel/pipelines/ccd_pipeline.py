"""TBW."""
from pyxel import util
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.detectors.detector import Detector
from pyxel.pipelines.model_group import ModelGroup


class CCDDetectionPipeline(DetectionPipeline):
    """TBW."""

    def __init__(self,
                 charge_transfer: ModelGroup,
                 **kwargs) -> None:
        """TBW.

        :param charge_transfer:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.charge_transfer = charge_transfer

        self._name = 'ccd'                                          # TODO
        self._model_groups = ['photon_generation',                  # TODO
                              'optics',
                              'charge_generation',
                              'charge_collection',
                              'charge_transfer',
                              'charge_measurement',
                              'readout_electronics']

        self._model_steps = {                                           # TODO
            'photon_generation':    ['load_image', 'photon_level',
                                     'shot_noise'],
            'optics':               [],
            'charge_generation':    ['photoelectrons',
                                     'tars'],
            'charge_collection':    ['fixed_pattern_noise',
                                     'full_well'],
            'charge_transfer':      ['cdm'],
            'charge_measurement':   ['output_node_noise'],
            'readout_electronics':  []
        }

    def copy(self):
        """TBW."""
        return CCDDetectionPipeline(**util.copy_state(self))

    def __getstate__(self):
        """TBW."""
        kwargs = super().__getstate__()
        kwargs_obj = {
            'charge_transfer': self.charge_transfer,
            '_name': self._name,                            # TODO
            '_model_groups': self._model_groups,            # TODO
            '_model_steps': self._model_steps               # TODO
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
        detector.pixels.fill_pixels_with_charges()
        detector = self.run_model_group('charge_collection', detector)

        # CHARGE TRANSFER:
        # -> transport/modify pixels ->
        detector = self.run_model_group('charge_transfer', detector)

        # CHARGE READOUT
        # -> create signal -> modify signal ->
        char = detector.characteristics
        detector.signal = detector.pixels.pixel_array * char.sv * char.amp * char.a1 * char.a2      # TODO
        # detector.signal = detector.signal.astype('float64')
        detector = self.run_model_group('charge_measurement', detector)

        # READOUT ELECTRONICS
        # -> create image -> modify image -> END
        # detector.image = detector.signal.astype('uint16')  # todo: replace this into detector class
        detector.image = detector.signal                     # todo: replace this into detector class   # TODO

        detector = self.run_model_group('readout_electronics', detector)  # todo: rounding signal in models
        # at this point the image pixel values should be rounded to integers (quantization)

        return detector
