#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest

import pyxel
from pyxel import Configuration
from pyxel.calibration import Algorithm, Calibration, CalibrationMode
from pyxel.data_structure import Charge, Image, Pixel, Signal
from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.exposure import Exposure
from pyxel.observation import Observation, ParameterMode
from pyxel.outputs.calibration_outputs import CalibrationOutputs
from pyxel.outputs.exposure_outputs import ExposureOutputs
from pyxel.outputs.observation_outputs import ObservationOutputs
from pyxel.pipelines import DetectionPipeline, ModelFunction, ModelGroup


@pytest.mark.parametrize(
    "yaml_file",
    [
        "tests/data/parametric.yaml",
        "tests/data/yaml.yaml",
        "tests/data/calibrate_models.yaml",
    ],
)
def test_yaml_load(yaml_file):
    cfg = pyxel.load(yaml_file)

    assert isinstance(cfg, Configuration)
    assert (
        isinstance(cfg.exposure, Exposure)
        or isinstance(cfg.calibration, Calibration)
        or isinstance(cfg.observation, Observation)
    )

    if isinstance(cfg.exposure, Exposure):
        assert isinstance(cfg.exposure.outputs, ExposureOutputs)
    elif isinstance(cfg.calibration, Calibration):
        assert isinstance(cfg.calibration.outputs, CalibrationOutputs)
        assert isinstance(cfg.calibration.algorithm, Algorithm)
        assert isinstance(cfg.calibration.calibration_mode, CalibrationMode)
    elif isinstance(cfg.observation, Observation):
        assert isinstance(cfg.observation.outputs, ObservationOutputs)
        assert isinstance(cfg.observation.parameter_mode, ParameterMode)

    assert isinstance(cfg.ccd_detector, CCD)
    assert isinstance(cfg.ccd_detector.geometry, CCDGeometry)
    assert isinstance(cfg.ccd_detector.characteristics, Characteristics)
    assert isinstance(cfg.ccd_detector.environment, Environment)
    assert isinstance(cfg.ccd_detector.image, Image)
    assert isinstance(cfg.ccd_detector.signal, Signal)
    assert isinstance(cfg.ccd_detector.pixel, Pixel)
    assert isinstance(cfg.ccd_detector.charge, Charge)

    assert isinstance(cfg.pipeline, DetectionPipeline)
    assert isinstance(cfg.pipeline.photon_collection, ModelGroup)
    assert isinstance(cfg.pipeline.photon_collection.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_generation, ModelGroup)
    assert isinstance(cfg.pipeline.charge_generation.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_collection, ModelGroup)
    assert isinstance(cfg.pipeline.charge_collection.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_transfer, ModelGroup)
    assert isinstance(cfg.pipeline.charge_transfer.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_measurement, ModelGroup)
    assert isinstance(cfg.pipeline.charge_measurement.models[0], ModelFunction)
