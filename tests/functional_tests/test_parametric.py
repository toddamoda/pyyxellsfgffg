#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from collections import abc
from pathlib import Path

import numpy as np
import pytest

import pyxel
from pyxel import Configuration
from pyxel.detectors import CCD
from pyxel.exposure import run_exposure_pipeline
from pyxel.observation import Observation, ParameterMode
from pyxel.pipelines import DetectionPipeline, Processor

expected_sequential = [
    (0, [("level", 10), ("initial_energy", 100)]),
    (1, [("level", 20), ("initial_energy", 100)]),
    (2, [("level", 30), ("initial_energy", 100)]),
    (3, [("level", 100), ("initial_energy", 100)]),
    (4, [("level", 100), ("initial_energy", 200)]),
    (5, [("level", 100), ("initial_energy", 300)]),
]

expected_product = [
    (0, [("level", 10), ("initial_energy", 100)]),
    (1, [("level", 10), ("initial_energy", 200)]),
    (2, [("level", 10), ("initial_energy", 300)]),
    (3, [("level", 20), ("initial_energy", 100)]),
    (4, [("level", 20), ("initial_energy", 200)]),
    (5, [("level", 20), ("initial_energy", 300)]),
    (6, [("level", 30), ("initial_energy", 100)]),
    (7, [("level", 30), ("initial_energy", 200)]),
    (8, [("level", 30), ("initial_energy", 300)]),
]


@pytest.mark.parametrize(
    "mode, expected",
    [
        # ('single', expected_single),
        (ParameterMode.Sequential, expected_sequential),
        (ParameterMode.Product, expected_product),
    ],
)
def test_pipeline_parametric_without_init_photon(mode: ParameterMode, expected):
    input_filename = "tests/data/parametric.yaml"
    cfg = pyxel.load(Path(input_filename))

    assert isinstance(cfg, Configuration)
    assert hasattr(cfg, "observation")
    assert hasattr(cfg, "ccd_detector")
    assert hasattr(cfg, "pipeline")

    observation = cfg.observation
    assert isinstance(observation, Observation)

    observation.parameter_mode = mode

    detector = cfg.ccd_detector
    assert isinstance(detector, CCD)

    pipeline = cfg.pipeline
    assert isinstance(pipeline, DetectionPipeline)

    processor = Processor(detector=detector, pipeline=pipeline)
    result = observation.debug_parameters(processor)
    assert result == expected

    detector.photon.array = np.zeros(detector.geometry.shape, dtype=float)
    detector.image.array = np.zeros(detector.geometry.shape, dtype=np.uint64)
    detector.pixel.array = np.zeros(detector.geometry.shape, dtype=float)
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)

    processor_generator = observation._processors_it(processor=processor)
    assert isinstance(processor_generator, abc.Generator)

    for proc, _, _ in processor_generator:
        assert isinstance(proc, Processor)

        run_exposure_pipeline(processor=proc, readout=observation.readout)


@pytest.mark.deprecated
@pytest.mark.parametrize(
    "mode, expected",
    [
        # ('single', expected_single),
        (ParameterMode.Sequential, expected_sequential),
        (ParameterMode.Product, expected_product),
    ],
)
def test_pipeline_parametric_without_init_photon_deprecated(
    mode: ParameterMode, expected
):
    input_filename = "tests/data/deprecated_parametric.yaml"
    cfg = pyxel.load(Path(input_filename))

    assert isinstance(cfg, Configuration)
    assert hasattr(cfg, "observation")
    assert hasattr(cfg, "ccd_detector")
    assert hasattr(cfg, "pipeline")

    observation = cfg.observation
    assert isinstance(observation, Observation)

    observation.parameter_mode = mode

    detector = cfg.ccd_detector
    assert isinstance(detector, CCD)

    pipeline = cfg.pipeline
    assert isinstance(pipeline, DetectionPipeline)

    processor = Processor(detector=detector, pipeline=pipeline)
    result = observation.debug_parameters(processor)
    assert result == expected

    detector.photon.array = np.zeros(detector.geometry.shape, dtype=float)
    detector.image.array = np.zeros(detector.geometry.shape, dtype=np.uint64)
    detector.pixel.array = np.zeros(detector.geometry.shape, dtype=float)
    detector.signal.array = np.zeros(detector.geometry.shape, dtype=float)

    processor_generator = observation._processors_it(processor=processor)
    assert isinstance(processor_generator, abc.Generator)

    for proc, _, _ in processor_generator:
        assert isinstance(proc, Processor)

        run_exposure_pipeline(processor=proc, readout=observation.readout)
