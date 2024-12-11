#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from pathlib import Path

import pytest

# Import 'DataTree'
try:
    from xarray.core.datatree import DataTree
except ImportError:
    from datatree import DataTree  # pip install xarray-datatree


from pyxel.calibration import (
    Algorithm,
    ArchipelagoDataTree,
    DaskBFE,
    DaskIsland,
    FitRange2D,
    FitRange3D,
)
from pyxel.calibration.fitness import sum_of_abs_residuals
from pyxel.calibration.fitting_datatree import ModelFittingDataTree
from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.exposure import Readout
from pyxel.observation import ParameterValues
from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor

# This is equivalent to 'import pygmo as pg'
pg = pytest.importorskip(
    "pygmo",
    reason="Package 'pygmo' is not installed. Use 'pip install pygmo'",
)


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


@pytest.mark.parametrize(
    "parallel",
    [
        pytest.param(True, id="with parallelization"),
        pytest.param(False, id="No parallelization"),
    ],
)
@pytest.mark.parametrize(
    "seed",
    [
        pytest.param(12345, id="with seed"),
        pytest.param(None, id="no seed"),
    ],
)
@pytest.mark.parametrize(
    "num_best_decisions",
    [
        pytest.param(10, id="with 'num_best_decisitions"),
        pytest.param(None, id="without 'num_best_decisitions"),
    ],
)
def test_archipelago_datatree(
    model_fitting: ModelFittingDataTree,
    processor: Processor,
    seed: int | None,
    parallel: bool,
    num_best_decisions: int | None,
):
    """Test class 'ArchipelagoDataTree'."""
    island = DaskIsland()
    batch_fitness_evaluator = DaskBFE()
    algo = Algorithm(type="sade", generations=10, population_size=20)
    topo = pg.fully_connected()

    archipelago = ArchipelagoDataTree(
        num_islands=1,
        udi=island,
        algorithm=algo,
        problem=model_fitting,
        pop_size=10,
        bfe=batch_fitness_evaluator,
        topology=topo,
        pygmo_seed=seed,
        parallel=parallel,
    )

    readout: Readout = model_fitting.readout
    dt = archipelago.run_evolve(
        readout=readout,
        num_rows=processor.detector.geometry.row,
        num_cols=processor.detector.geometry.col,
        num_evolutions=1,
        num_best_decisions=num_best_decisions,
    )
    assert isinstance(dt, DataTree)
