import typing as t  # noqa: F401

from pyxel.detectors.ccd import CCD
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

    def __init__(self, ccd: CCD, pipeline: DetectionPipeline) -> None:
        self.ccd = ccd
        self.pipeline = pipeline


def run_pipeline(detector: CCD, pipeline: DetectionPipeline) -> CCD:

    # OPTICS
    detector.photons = Photon(detector)
    detector.generate_incident_photons()

    # Stage 1: Apply the Optics model(s). only '.photons' is modified
    steps = ['shot_noise', 'ray_tracing', 'diffraction']
    for step in steps:
        func = pipeline.optics.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE GENERATION
    detector.charges = Charge(detector)

    steps = ['photoelectrons']  # , 'fixed_pattern_noise', 'tars', 'xray', 'snowballs']
    for step in steps:
        func = pipeline.charge_generation.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE COLLECTION
    detector.pixels = Pixel(detector)
    detector.pixels.fill_with_charge()

    steps = []  # ['diffusion']
    for step in steps:
        func = pipeline.charge_collection.models.get(step)
        if func:
            detector = func(detector)

    detector.pixels.charge_excess()

    # CHARGE TRANSFER
    steps = []
    for step in steps:
        func = pipeline.charge_transfer.models.get(step)
        if func:
            detector = func(detector)

    # CHARGE READOUT
    # detector.compute_signal()
    # TODO: Convert here the charge object list into a 2d signal array

    steps = ['output_node_noise']
    for step in steps:
        func = pipeline.charge_readout.models.get(step)
        if func:
            detector = func(detector)

    # READOUT ELECTRONICS
    detector.compute_readout_signal()
    steps = []
    for step in steps:
        func = pipeline.readout_electronics.models.get(step)
        if func:
            detector = func(detector)

    return detector
