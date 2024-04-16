#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import math
from pathlib import Path

import numpy as np
import pytest

from pyxel.calibration import FitRange2D, FitRange3D
from pyxel.calibration.fitness import sum_of_abs_residuals
from pyxel.calibration.fitting_datatree import ModelFittingDataTree
from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.exposure import Readout
from pyxel.observation.parameter_values import ParameterValues
from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor


@pytest.fixture
def model_fitting() -> ModelFittingDataTree:
    detector = CCD(
        geometry=CCDGeometry(row=835, col=1),
        environment=Environment(temperature=238.0),
        characteristics=Characteristics(full_well_capacity=90_0000),
    )
    pipeline = DetectionPipeline(
        charge_transfer=[
            ModelFunction(
                func="pyxel.models.charge_transfer.cdm",
                name="cdm",
                arguments={
                    "direction": "parallel",
                    "trap_release_times": [5.0e-3, 5.0e-3, 5.0e-3, 5.0e-3],
                    "trap_densities": [1.0, 1.0, 1.0, 1.0],
                    "sigma": [1.0e-15, 1.0e-15, 1.0e-15, 1.0e-15],
                    "beta": 0.3,  # calibrating this parameter
                    "max_electron_volume": 1.62e-10,  # cm^2
                    "transfer_period": 9.4722e-04,  # s
                    "charge_injection": True,
                },
            )
        ]
    )
    processor = Processor(detector=detector, pipeline=pipeline)
    folder = Path("tests/observation")

    return ModelFittingDataTree(
        processor=processor,
        variables=[
            ParameterValues(
                key="pipeline.charge_transfer.cdm.arguments.beta",
                values="_",
                logarithmic=False,
                boundaries=(0.1, 0.9),
            ),
            ParameterValues(
                key="pipeline.charge_transfer.cdm.arguments.trap_release_times",
                values=["_", "_", "_", "_"],
                logarithmic=True,
                boundaries=(1e-5, 1e-1),
            ),
            ParameterValues(
                key="pipeline.charge_transfer.cdm.arguments.trap_densities",
                values=["_", "_", "_", "_"],
                logarithmic=True,
                boundaries=(1e-2, 1e2),
            ),
        ],
        readout=Readout(),
        simulation_output="pixel",
        generations=10,
        population_size=20,
        fitness_func=sum_of_abs_residuals,
        file_path=None,
        target_fit_range=FitRange2D(row=slice(500, 835), col=slice(0, 1)),
        out_fit_range=FitRange3D(
            time=slice(None, None), row=slice(500, 835), col=slice(0, 1)
        ),
        target_filenames=[
            folder / "data/target/target_flex_ds7_ch0_1ke.txt",
            folder / "data/target/target_flex_ds7_ch0_3ke.txt",
            folder / "data/target/target_flex_ds7_ch0_7ke.txt",
            folder / "data/target/target_flex_ds7_ch0_10ke.txt",
            folder / "data/target/target_flex_ds7_ch0_20ke.txt",
            folder / "data/target/target_flex_ds7_ch0_100ke.txt",
        ],
    )


def test_get_bounds(model_fitting: ModelFittingDataTree):
    """Test method 'ModelFittingDataTree.get_bounds()'."""
    bounds = model_fitting.get_bounds()
    assert bounds == (
        ([0.1] + [math.log10(1e-5)] * 4 + [math.log10(1e-2)] * 4),
        ([0.9] + [math.log10(1e-1)] * 4 + [math.log10(1e2)] * 4),
    )


def test_fitness(model_fitting: ModelFittingDataTree):
    """Test method 'ModelFittingDataTree.fitness()."""
    result = model_fitting.fitness(
        decision_vector_1d=np.array([0.5, -3.0, -3.0, -3.0, -3.0, 0.0, 0.0, 0.0, 0.0])
    )
    assert result == [117566.16148236669]
