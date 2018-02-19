"""TBW."""

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

        self._model_groups = ['optics', 'charge_generation', 'charge_collection',
                              'charge_measurement', 'signal_transfer', 'readout_electronics']

        self._model_steps = {
            'optics': ['shot_noise'],
            'charge_generation': ['photoelectrons', 'tars'],
            'charge_collection': ['fixed_pattern_noise'],
            'charge_measurement': ['output_node_noise'],
            'signal_transfer': ['nghxrg_read', 'nghxrg_ktc_bias', 'nghxrg_u_pink', 'nghxrg_c_pink',
                                'nghxrg_acn', 'nghxrg_pca_zero'],
            'readout_electronics': []
        }

    def run_pipeline(self, detector: Detector) -> Detector:
        """TBW."""
        # INITIALIZATION (open or generate image):
        # START -> create photons ->
        photon_numbers, photon_energies = detector.initialize_detector()
        detector.photons = Photon(detector)
        detector.photons.generate_photons(photon_numbers, photon_energies)

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
        detector = self.run_model_group('charge_measurement', detector)
        detector = self.run_model_group('signal_transfer', detector)

        # READOUT ELECTRONICS
        # -> create image -> modify image -> END
        detector = self.run_model_group('readout_electronics', detector)

        return detector
