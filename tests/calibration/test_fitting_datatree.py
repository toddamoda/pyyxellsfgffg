#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import math
from pathlib import Path

import dask
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from pyxel.calibration import FitRange2D, FitRange3D
from pyxel.calibration.fitness import sum_of_abs_residuals
from pyxel.calibration.fitting_datatree import ModelFittingDataTree
from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.exposure import Readout
from pyxel.observation import ParameterValues
from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor


@pytest.fixture
def ccd_detector() -> CCD:
    return CCD(
        geometry=CCDGeometry(row=835, col=1),
        environment=Environment(temperature=238.0),
        characteristics=Characteristics(full_well_capacity=90_0000),
    )


@pytest.fixture
def pipeline() -> DetectionPipeline:
    return DetectionPipeline(
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


@pytest.fixture
def processor(ccd_detector: CCD, pipeline: DetectionPipeline) -> Processor:
    return Processor(detector=ccd_detector, pipeline=pipeline)


@pytest.fixture
def parameter_values_lst() -> list[ParameterValues]:
    return [
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
    ]


@pytest.fixture
def model_fitting(
    processor: Processor, parameter_values_lst: list[ParameterValues]
) -> ModelFittingDataTree:
    folder = Path("tests/observation")

    return ModelFittingDataTree(
        processor=processor,
        variables=parameter_values_lst,
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


def test_model_fitting_data_tree_with_input_arguments(
    processor: Processor, parameter_values_lst: list[ParameterValues]
):
    """Test 'ModelFittingDataTree.__init__' with parameter 'input_arguments'."""
    folder = Path("tests/observation")
    _ = ModelFittingDataTree(
        processor=processor,
        variables=parameter_values_lst,
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
        input_arguments=[
            ParameterValues(
                key="pipeline.charge_transfer.cdm.arguments.trap_release_times",
                values=[0.01, 0.01, 0.01, 0.01],
                logarithmic=True,
                boundaries=(1e-5, 1e-1),
            )
        ],
    )


# TODO: This should be of, fix this !
@pytest.mark.fix_this
def test_model_fitting_data_tree_with_invalid_arguments(
    processor: Processor, parameter_values_lst: list[ParameterValues]
):
    """Test 'ModelFittingDataTree.__init__' with parameter 'input_arguments'."""
    folder = Path("tests/observation")
    with pytest.raises(
        ValueError, match="Parameter values cannot be initiated with those values"
    ):
        _ = ModelFittingDataTree(
            processor=processor,
            variables=parameter_values_lst,
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
            input_arguments=[
                ParameterValues(
                    key="pipeline.charge_transfer.cdm.arguments.beta",
                    values=0.5,
                    logarithmic=False,
                    boundaries=(0.1, 0.9),
                )
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


def test_apply_parameters_to_processors(model_fitting: ModelFittingDataTree):
    """Test method 'ModelFittingDataTree.apply_parameters_to_processors'."""
    params = xr.DataArray(
        [[0.5, 6.9e-3, 1.7e-4, 5.4e-3, 1.0e-3, 1.5e1, 8.2, 1.2e1, 9.4e-2]],
        dims=["island", "param_id"],
        coords={
            "island": [0],
            "param_id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
        },
    )

    df = model_fitting.apply_parameters_to_processors(parameters=params)
    assert isinstance(df, pd.DataFrame)
    assert "data_tree" in df

    lst = df["data_tree"].to_list()
    _ = dask.compute(lst)


@pytest.mark.parametrize(
    "params, exp_exc, exp_msg",
    [
        pytest.param(
            xr.DataArray(
                [[3e-1, 6e-3, 1e-4, 5e-3, 1e-3, 1.5e1, 8.2, 1.2e1, 9.4e-2]],
                dims=["island", "foo"],
                coords={
                    "island": [0],
                    "foo": [0, 1, 2, 3, 4, 5, 6, 7, 8],
                },
            ),
            KeyError,
            r"Missing dimension 'param_id'",
        ),
        pytest.param(
            xr.DataArray(
                [[3e-1, 6e-3, 1e-4, 5e-3, 1e-3, 1.5e1, 8.2, 1.2e1, 9.4e-2]],
                dims=["foo", "param_id"],
                coords={
                    "foo": [0],
                    "param_id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
                },
            ),
            KeyError,
            r"Missing dimension 'island'",
        ),
    ],
)
def test_apply_parameters_to_processors_with_wrong_inputs(
    model_fitting: ModelFittingDataTree,
    params: xr.DataArray,
    exp_exc: type[Exception],
    exp_msg: str,
):
    """Test method 'ModelFittingDataTree.apply_parameters_to_processors'."""
    with pytest.raises(exp_exc, match=exp_msg):
        _ = model_fitting.apply_parameters_to_processors(parameters=params)
