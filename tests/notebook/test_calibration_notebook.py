#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from pathlib import Path

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from pyxel.calibration import Algorithm, Calibration, sum_of_abs_residuals
from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.notebook import (
    champion_heatmap,
    display_calibration_inputs,
    display_evolution,
    display_simulated,
    optimal_parameters,
)
from pyxel.observation import ParameterValues


def test_display_calibration_inputs():
    """Test function 'display_calibration_inputs'."""
    folder = Path("tests/observation")

    detector = CCD(
        geometry=CCDGeometry(row=10, col=10),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    calibration = Calibration(
        target_data_path=[
            folder / "data/target/target_flex_ds7_ch0_1ke.txt",
            folder / "data/target/target_flex_ds7_ch0_3ke.txt",
            folder / "data/target/target_flex_ds7_ch0_7ke.txt",
            folder / "data/target/target_flex_ds7_ch0_10ke.txt",
            folder / "data/target/target_flex_ds7_ch0_20ke.txt",
            folder / "data/target/target_flex_ds7_ch0_100ke.txt",
        ],
        fitness_function=sum_of_abs_residuals,
        algorithm=Algorithm(type="sade", generations=10, population_size=20),
        parameters=[
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
        result_input_arguments=[
            ParameterValues(
                key="pipeline.charge_generation.load_charge.arguments.filename",
                values=[
                    "data/input/input_flex_ds7_ch0_1ke.txt",
                    "data/input/input_flex_ds7_ch0_3ke.txt",
                    "data/input/input_flex_ds7_ch0_7ke.txt",
                    "data/input/input_flex_ds7_ch0_10ke.txt",
                    "data/input/input_flex_ds7_ch0_20ke.txt",
                    "data/input/input_flex_ds7_ch0_100ke.txt",
                ],
            ),
        ],
        result_fit_range=(500, 835, 0, 1),
        target_fit_range=(500, 835, 0, 1),
    )

    layout = display_calibration_inputs(calibration=calibration, detector=detector)
    assert isinstance(layout, hv.Layout)


@pytest.fixture(params=["old_format - xy", "old_format - y", "old_format - x"])
def dataset(request: pytest.FixtureRequest) -> xr.Dataset:
    rng = np.random.default_rng(seed=12345)

    if request.param == "old_format - xy":
        # Old format with x and y
        ds = xr.Dataset(
            coords={
                "y": [500, 501],
                "island": [0, 1],
                "evolution": [0, 1],
                "individual": [0, 1],
                "param_id": [0, 1],
                "id_processor": [0, 1],
                "x": [0, 1],
            },
            attrs={
                "num_islands": 160,
                "population_size": 250,
                "num_evolutions": 125,
                "generations": 20,
                "topology": "fully_connected",
                "result_type": "ResultType.Pixel",
            },
        )
        ds["simulated_image"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)), dims=["island", "id_processor", "y", "x"]
        )
        ds["simulated_signal"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)), dims=["island", "id_processor", "y", "x"]
        )
        ds["simulated_pixel"] = xr.DataArray(
            rng.integers(low=0, high=2**16, size=(2, 2, 2, 2)),
            dims=["island", "id_processor", "y", "x"],
        )
        ds["best_decision"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)),
            dims=["evolution", "island", "individual", "param_id"],
        )
        ds["best_parameters"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)),
            dims=["evolution", "island", "individual", "param_id"],
        )
        ds["best_fitness"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "individual"]
        )
        ds["champion_decision"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "param_id"]
        )
        ds["champion_parameters"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "param_id"]
        )
        ds["champion_fitness"] = xr.DataArray(
            rng.random(size=(2, 2)), dims=["evolution", "island"]
        )
        ds["target"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["id_processor", "y", "x"]
        )

        return ds
    elif request.param == "old_format - y":
        # Old format only y
        ds = xr.Dataset(
            coords={
                "y": [500, 501],
                "island": [0, 1],
                "evolution": [0, 1],
                "individual": [0, 1],
                "param_id": [0, 1],
                "id_processor": [0, 1],
                "x": [0],
            },
            attrs={
                "num_islands": 160,
                "population_size": 250,
                "num_evolutions": 125,
                "generations": 20,
                "topology": "fully_connected",
                "result_type": "ResultType.Pixel",
            },
        )
        ds["simulated_image"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 1)), dims=["island", "id_processor", "y", "x"]
        )
        ds["simulated_signal"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 1)), dims=["island", "id_processor", "y", "x"]
        )
        ds["simulated_pixel"] = xr.DataArray(
            rng.integers(low=0, high=2**16, size=(2, 2, 2, 1)),
            dims=["island", "id_processor", "y", "x"],
        )
        ds["best_decision"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)),
            dims=["evolution", "island", "individual", "param_id"],
        )
        ds["best_parameters"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)),
            dims=["evolution", "island", "individual", "param_id"],
        )
        ds["best_fitness"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "individual"]
        )
        ds["champion_decision"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "param_id"]
        )
        ds["champion_parameters"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "param_id"]
        )
        ds["champion_fitness"] = xr.DataArray(
            rng.random(size=(2, 2)), dims=["evolution", "island"]
        )
        ds["target"] = xr.DataArray(
            rng.random(size=(2, 2, 1)), dims=["id_processor", "y", "x"]
        )

        return ds
    elif request.param == "old_format - x":
        ds = xr.Dataset(
            coords={
                "y": [0],
                "island": [0, 1],
                "evolution": [0, 1],
                "individual": [0, 1],
                "param_id": [0, 1],
                "id_processor": [0, 1],
                "x": [0, 1],
            },
            attrs={
                "num_islands": 160,
                "population_size": 250,
                "num_evolutions": 125,
                "generations": 20,
                "topology": "fully_connected",
                "result_type": "ResultType.Pixel",
            },
        )
        ds["simulated_image"] = xr.DataArray(
            rng.random(size=(2, 2, 1, 2)), dims=["island", "id_processor", "y", "x"]
        )
        ds["simulated_signal"] = xr.DataArray(
            rng.random(size=(2, 2, 1, 2)), dims=["island", "id_processor", "y", "x"]
        )
        ds["simulated_pixel"] = xr.DataArray(
            rng.integers(low=0, high=2**16, size=(2, 2, 1, 2)),
            dims=["island", "id_processor", "y", "x"],
        )
        ds["best_decision"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)),
            dims=["evolution", "island", "individual", "param_id"],
        )
        ds["best_parameters"] = xr.DataArray(
            rng.random(size=(2, 2, 2, 2)),
            dims=["evolution", "island", "individual", "param_id"],
        )
        ds["best_fitness"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "individual"]
        )
        ds["champion_decision"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "param_id"]
        )
        ds["champion_parameters"] = xr.DataArray(
            rng.random(size=(2, 2, 2)), dims=["evolution", "island", "param_id"]
        )
        ds["champion_fitness"] = xr.DataArray(
            rng.random(size=(2, 2)), dims=["evolution", "island"]
        )
        ds["target"] = xr.DataArray(
            rng.random(size=(2, 1, 2)), dims=["id_processor", "y", "x"]
        )

        return ds

    else:
        raise NotImplementedError


def test_display_simulated(dataset: xr.Dataset):
    """Test function 'display_simulated'."""
    layout = display_simulated(ds=dataset)
    assert isinstance(layout, hv.Layout)


def test_display_evolution(dataset: xr.Dataset):
    """Test function 'display_evolution'."""
    layout = display_evolution(ds=dataset)
    assert isinstance(layout, hv.Layout)


def test_optimal_parameters(dataset: xr.Dataset):
    """Test function 'optimal_parameters'."""
    df = optimal_parameters(ds=dataset)
    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize("parameter_range", [None, (0, 1)])
@pytest.mark.parametrize("island_range", [None, (0, 1)])
@pytest.mark.parametrize("ind_range", [None, (0, 1)])
@pytest.mark.parametrize("logx", [False, True])
def test_champion_heatmap(
    dataset: xr.Dataset,
    parameter_range: tuple[int, int] | None,
    island_range: tuple[int, int] | None,
    ind_range: tuple[int, int] | None,
    logx: bool,
):
    """Test function 'champion_heatmap'."""
    points = champion_heatmap(
        ds=dataset,
        parameter_range=parameter_range,
        island_range=island_range,
        ind_range=ind_range,
        logx=logx,
    )
    assert isinstance(points, hv.Points)
