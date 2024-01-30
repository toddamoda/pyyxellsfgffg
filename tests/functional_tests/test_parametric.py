#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import logging
from collections import abc
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import pyxel
from pyxel import Configuration
from pyxel.detectors import CCD
from pyxel.exposure import run_exposure_pipeline
from pyxel.observation import Observation, ParameterMode
from pyxel.pipelines import DetectionPipeline, Processor
from pyxel.pipelines.processor import _get_obj_att

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


def get_value(obj: Any, key: str) -> Any:
    """Retrieve the attribute value of the object given the attribute dot formatted key chain.

    Example::

        >>> obj = {"processor": {"pipeline": {"models": [1, 2, 3]}}}
        >>> om.get_value(obj, "processor.pipeline.models")
        [1, 2, 3]

    The above example works as well for a user-defined object with a attribute
    objects, i.e. configuration object model.
    """
    obj, att = _get_obj_att(obj, key)

    if isinstance(obj, dict) and att in obj:
        value = obj[att]
    else:
        value = getattr(obj, att)

    return value


def debug_parameters(observation: Observation, processor: Processor) -> list:
    """List the parameters using processor parameters in processor generator."""
    result = []
    processor_generator = observation._processors_it(processor=processor)
    for i, (proc, _, _) in enumerate(processor_generator):
        values = []
        for step in observation.enabled_steps:
            _, att = _get_obj_att(proc, step.key)
            value = get_value(proc, step.key)
            values.append((att, value))
        logging.debug("%d: %r", i, values)
        result.append((i, values))
    return result


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
    result = debug_parameters(observation=observation, processor=processor)
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
