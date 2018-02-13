from pyxel.detectors.ccd import CCD
from pyxel.physics.charge import Charge
from pyxel.physics.photon import Photon
from pyxel.physics.pixel import Pixel
from pyxel.pipelines.models import Models


class CCDDetectionPipeline:

    def __init__(self,
                 optics: Models,
                 charge_generation: Models,
                 charge_collection: Models,
                 charge_transfer: Models,
                 charge_measurement: Models,
                 readout_electronics: Models,
                 doc=None) -> None:
        self.doc = doc
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_transfer = charge_transfer
        self.charge_measurement = charge_measurement
        self.readout_electronics = readout_electronics

    def run_pipeline(self, detector: CCD) -> CCD:

        # INITIALIZATION (open or generate image):
        # START -> create photons ->
        photon_numbers, photon_energies = detector.initialize_detector()

        detector.photons = Photon(detector)
        detector.photons.generate_photons(photon_numbers, photon_energies)

        # OPTICS:
        # -> transport/modify photons ->
        steps = ['shot_noise']  # , 'ray_tracing', 'diffraction']
        for step in steps:
            func = self.optics.models.get(step)
            if func:
                detector = func(detector)

        # CHARGE GENERATION:
        # -> create charges & remove photons ->
        detector.charges = Charge(detector)

        steps = ['photoelectrons', 'tars']   # 'xray', 'snowballs']
        for step in steps:
            func = self.charge_generation.models.get(step)
            if func:
                detector = func(detector)

        # CHARGE COLLECTION:
        # -> transport/modify charges ->
        # -> collect charges in pixels ->
        detector.pixels = Pixel(detector)
        detector.pixels.generate_pixels()

        steps = ['fixed_pattern_noise', 'full_well']  # ['diffusion', ... , 'full_well']
        for step in steps:
            func = self.charge_collection.models.get(step)
            if func:
                detector = func(detector)

        # CHARGE TRANSFER:
        # -> transport/modify pixels ->

        steps = ['cdm']  # ['cdm']
        for step in steps:
            func = self.charge_transfer.models.get(step)
            if func:
                detector = func(detector)

        # CHARGE READOUT
        # -> create signal -> modify signal ->
        detector.signal = detector.pixels.generate_2d_charge_array()

        steps = ['output_node_noise']
        for step in steps:
            func = self.charge_measurement.models.get(step)
            if func:
                detector = func(detector)

        # READOUT ELECTRONICS
        # -> create image -> modify image -> END
        # detector.image = detector.signal.generate_image()

        steps = []
        for step in steps:
            func = self.readout_electronics.models.get(step)
            if func:
                detector = func(detector)

        return detector
