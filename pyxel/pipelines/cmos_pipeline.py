"""TBW."""
from pyxel import util
from pyxel.pipelines.detector_pipeline import DetectionPipeline
from pyxel.detectors.detector import Detector
from pyxel.physics.charge import Charge
from pyxel.physics.photon import Photon
from pyxel.physics.pixel import Pixel
from pyxel.pipelines.models import Models


class CMOSDetectionPipeline(DetectionPipeline):
    """TBW."""

    def __init__(self,
                 signal_transfer: Models,
                 **kwargs) -> None:
        """TBW.

        :param signal_transfer:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.signal_transfer = signal_transfer

        self._model_groups = ['photon_generation', 'optics', 'charge_generation', 'charge_collection',
                              'charge_measurement', 'signal_transfer', 'readout_electronics']

        self._model_steps = {
            'photon_generation':    ['load_image', 'photon_level',
                                     'shot_noise'],
            'optics':               [],
            'charge_generation':    ['photoelectrons',
                                     'tars'],
            'charge_collection':    ['full_well'],
            'charge_measurement':   ['nghxrg_ktc_bias',
                                     'nghxrg_read'],
            'signal_transfer':      ['nghxrg_acn',
                                     'nghxrg_u_pink',
                                     'nghxrg_c_pink'],
            'readout_electronics':  ['nghxrg_pca_zero']
        }

    def copy(self):
        """TBW."""
        # kwargs = {key: value.copy() if value else None for key, value in self.__getstate__().items()}
        # kwargs = {
        #     'signal_transfer': self.signal_transfer.copy(),
        # }
        # for key in super().__getstate__():
        #     kwargs[key] = getattr(cpy, key).copy()
        return CMOSDetectionPipeline(**util.copy_state(self))

    def __getstate__(self):
        """TBW."""
        kwargs = super().__getstate__()
        kwargs_obj = {
            'signal_transfer': self.signal_transfer
        }
        return {**kwargs, **kwargs_obj}

    def run_pipeline(self, detector: Detector) -> Detector:
        """TBW."""
        # INITIALIZATION (open or generate image):
        # START -> create photons ->
        detector.photons = Photon(detector)
        # detector.photons.generate_photons()
        detector = self.run_model_group('photon_generation', detector)

        # OPTICS:
        # -> transport/modify photons ->
        detector = self.run_model_group('optics', detector)

        # CHARGE GENERATION:
        # -> create charges & remove photons ->
        detector.charges = Charge(detector)
        detector = self.run_model_group('charge_generation', detector)

        # CHARGE COLLECTION:
        # -> transport/modify charges ->
        # -> collect charges in pixels ->
        detector.pixels = Pixel(detector)
        detector.pixels.generate_pixels()
        detector = self.run_model_group('charge_collection', detector)

        # CHARGE READOUT
        # -> create signal -> modify signal ->
        detector.signal = detector.pixels.generate_2d_charge_array()
        detector.signal = detector.signal.astype('float64')

        detector = self.run_model_group('charge_measurement', detector)
        detector = self.run_model_group('signal_transfer', detector)

        # READOUT ELECTRONICS
        # -> create image -> modify image -> END
        detector = self.run_model_group('readout_electronics', detector)

        return detector
