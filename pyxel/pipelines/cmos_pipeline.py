from pyxel.detectors.cmos import CMOS
from pyxel.physics.charge import Charge
from pyxel.physics.photon import Photon
from pyxel.physics.pixel import Pixel
from pyxel.pipelines.models import Models


class CMOSDetectionPipeline:

    def __init__(self,
                 optics: Models,
                 charge_generation: Models,
                 charge_collection: Models,
                 charge_measurement: Models,
                 signal_transfer: Models,
                 readout_electronics: Models,
                 doc=None) -> None:
        self.doc = doc
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_measurement = charge_measurement
        self.signal_transfer = signal_transfer
        self.readout_electronics = readout_electronics

    def run_pipeline(self, detector: CMOS) -> CMOS:

        # INITIALIZATION (open or generate image):
        # START -> create photons ->
        photon_numbers, photon_energies = detector.initialize_detector()

        detector.photons = Photon(detector)
        detector.photons.generate_photons(photon_numbers, photon_energies)

        # OPTICS:
        # -> transport/modify photons ->
        steps = []  # type: list    # ['shot_noise']  # , 'ray_tracing', 'diffraction']
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

        steps = []  # ['fixed_pattern_noise']  # ['diffusion', ... , 'full_well']
        for step in steps:
            func = self.charge_collection.models.get(step)
            if func:
                detector = func(detector)

        # CHARGE MEASUREMENT
        # -> create signal ->
        detector.signal = detector.pixels.generate_2d_charge_array()

        steps = []  # ['output_node_noise']
        for step in steps:
            func = self.charge_measurement.models.get(step)
            if func:
                detector = func(detector)

        # SIGNAL TRANSFER
        # -> modify signal ->

        steps = ['nghxrg_read', 'nghxrg_ktc_bias', 'nghxrg_u_pink', 'nghxrg_c_pink', 'nghxrg_acn', 'nghxrg_pca_zero']
        for step in steps:
            func = self.signal_transfer.models.get(step)
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
