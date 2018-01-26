import typing as t  # noqa: F401

from pyxel.detectors.ccd import CCD
from pyxel.detectors.cmos import CMOS
from pyxel.util import util
from pyxel.physics.charge import Charge
from pyxel.physics.photon import Photon
from pyxel.physics.pixel import Pixel


class Models:

    def __init__(self, models: dict) -> None:

        new_dct = {}
        for key, value in models.items():

            if isinstance(value, str):
                func = util.evaluate_reference(value)  # type: t.Callable

            elif callable(value):
                func = value

            else:
                raise NotImplementedError

            new_dct[key] = func

        self.models = new_dct                   # type: t.Dict[str, t.Callable]


class DetectionPipeline:

    def __init__(self,
                 optics: Models,
                 charge_generation: Models,
                 charge_collection: Models,
                 charge_transfer: Models,
                 charge_readout: Models,
                 readout_electronics: Models,
                 doc=None) -> None:
        self.doc = doc
        self.optics = optics
        self.charge_generation = charge_generation
        self.charge_collection = charge_collection
        self.charge_transfer = charge_transfer
        self.charge_readout = charge_readout
        self.readout_electronics = readout_electronics


class Processor:

    def __init__(self, cmos: CMOS, pipeline: DetectionPipeline) -> None:
        self.cmos = cmos
        self.pipeline = pipeline


# class Processor:
#
#     def __init__(self, ccd: CCD, pipeline: DetectionPipeline) -> None:
#         self.ccd = ccd
#         self.pipeline = pipeline


# def run_pipeline(detector: CCD, pipeline: DetectionPipeline) -> CCD:
def run_pipeline(detector: CMOS, pipeline: DetectionPipeline) -> CCD:

    # INITIALIZATION (open or generate image):
    # START -> create photons ->
    photon_numbers, photon_energies = detector.initialize_detector()

    detector.photons = Photon(detector)
    detector.photons.generate_photons(photon_numbers, photon_energies)

    # OPTICS:
    # -> transport/modify photons ->
    steps = ['shot_noise']  # , 'ray_tracing', 'diffraction']
    for step in steps:
        func = pipeline.optics.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE GENERATION:
    # -> create charges & remove photons ->
    detector.charges = Charge(detector)

    steps = ['photoelectrons', 'tars']   # 'xray', 'snowballs']
    for step in steps:
        func = pipeline.charge_generation.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE COLLECTION:
    # -> transport/modify charges ->
    # -> collect charges in pixels ->
    detector.pixels = Pixel(detector)
    detector.pixels.generate_pixels()

    steps = ['fixed_pattern_noise', 'full_well']  # ['diffusion', ... , 'full_well']
    for step in steps:
        func = pipeline.charge_collection.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE TRANSFER:
    # -> transport/modify pixels ->

    steps = []  # ['cdm']
    for step in steps:
        func = pipeline.charge_transfer.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE READOUT
    # -> create signal -> modify signal ->
    detector.signal = detector.pixels.generate_signal()

    steps = ['output_node_noise']
    for step in steps:
        func = pipeline.charge_readout.models.get(step)
        if func:
            detector = func(detector)

    # READOUT ELECTRONICS
    # -> create image -> modify image -> END
    # detector.image = detector.signal.generate_image()

    steps = []
    for step in steps:
        func = pipeline.readout_electronics.models.get(step)
        if func:
            detector = func(detector)

    return detector
