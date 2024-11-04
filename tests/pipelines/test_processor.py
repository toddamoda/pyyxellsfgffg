#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor


@pytest.fixture
def ccd_detector() -> CCD:
    return CCD(
        geometry=CCDGeometry(row=10, col=20),
        environment=Environment(temperature=238.0),
        characteristics=Characteristics(full_well_capacity=90_0000),
    )


@pytest.fixture
def pipeline1() -> DetectionPipeline:
    return DetectionPipeline(
        photon_collection=[
            ModelFunction(
                func="pyxel.models.photon_collection.stripe_pattern",
                name="stripe_pattern",
                arguments={"level": 1_0000, "period": 10, "startwith": 0, "angle": 5},
            ),
            ModelFunction(
                func="pyxel.models.photon_collection.stripe_pattern",
                name="other_stripe_pattern",
                arguments={"level": 1_0000, "period": 10, "startwith": 0, "angle": 5},
            ),
        ],
        charge_transfer=[
            ModelFunction(
                func="pyxel.models.charge_transfer.cdm",
                name="cdm",
                arguments={
                    "direction": "parallel",
                    "trap_release_times": [3.0e-3, 3.0e-2],
                    "trap_densities": [60.0, 100],
                    "sigma": [1.0e-10, 1.0e-10],
                    "beta": 0.3,
                    "max_electron_volume": 1.62e-10,  # cm^2
                    "transfer_period": 9.4722e-04,  # s
                    "charge_injection": True,
                },
            ),
        ],
    )


@pytest.fixture
def processor1(ccd_detector: CCD, pipeline1: DetectionPipeline) -> Processor:
    return Processor(detector=ccd_detector, pipeline=pipeline1)


def test_repr(processor1: Processor):
    """Test method 'Processor.__repr__'."""
    processor: Processor = processor1

    assert repr(processor).startswith("Processor<detector=")


@pytest.mark.parametrize(
    "key, exp_result",
    [
        ("detector.geometry.row", True),
        ("detector.environment.temperature", True),
        ("detector.characteristics.quantum_efficiency", True),
        ("detector.photon.array", True),
        ("detector.image.array", True),
        ("pipeline", True),
        ("pipeline.photon_collection", True),
        ("pipeline.photon_collection.shot_noise", False),
        ("pipeline.photon_collection.stripe_pattern", True),
        ("pipeline.photon_collection.stripe_pattern.angle", False),
        ("pipeline.photon_collection.stripe_pattern.arguments.angle", True),
        # Non-existing parameters
        ("detector.geometry.rows", False),
        ("detector.image.foo", False),
        ("detector.foo.array", False),
        ("foo.photon.array", False),
    ],
)
def test_has(processor1: Processor, key, exp_result):
    """Test method 'Processor.has'."""
    processor: Processor = processor1

    assert processor.has(key) is exp_result


@pytest.mark.parametrize(
    "key, exp_result",
    [
        ("detector.geometry.row", 10),
        ("detector.environment.temperature", 238.0),
        ("detector.characteristics.full_well_capacity", 90_0000),
        ("pipeline.photon_collection.stripe_pattern.arguments.angle", 5.0),
    ],
)
def test_get(processor1: Processor, key, exp_result):
    """Test method 'Processor.get'."""
    processor: Processor = processor1

    result = processor.get(key)
    assert result == exp_result


@pytest.mark.parametrize(
    "key, value",
    [
        ("detector.environment.temperature", 123.0),
        ("detector.characteristics.full_well_capacity", 456),
        ("pipeline.photon_collection.stripe_pattern.arguments.angle", 3.14),
    ],
)
def test_set(processor1: Processor, key, value):
    """Test method 'Processor.set'."""
    processor: Processor = processor1

    processor.set(key, value)
    result = processor.get(key)

    assert result == value
