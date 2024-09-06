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


from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.observation import Observation, ParameterValues
from pyxel.outputs import ObservationOutputs
from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor


@pytest.fixture(
    params=["product_parameters", "product_parameters_duplicate"],
)
def product_parameter_values_lst(request) -> list[ParameterValues]:
    if request.param == "product_parameters":
        return [
            ParameterValues(
                key="pipeline.photon_collection.stripe_pattern.arguments.period",
                values="numpy.linspace(4, 20, 2, dtype=int)",
            ),
            ParameterValues(
                key="pipeline.photon_collection.stripe_pattern.arguments.angle",
                values=[0, 10],
            ),
            ParameterValues(
                key="pipeline.charge_transfer.cdm.arguments.trap_densities",
                values=[[10, 20], [20, 30]],
            ),
        ]
    elif request.param == "product_parameters_duplicate":
        return [
            ParameterValues(
                key="pipeline.photon_collection.stripe_pattern.arguments.period",
                values="numpy.linspace(4, 20, 2, dtype=int)",
            ),
            ParameterValues(
                key="pipeline.photon_collection.other_stripe_pattern.arguments.period",
                values=[4, 6],
            ),
            ParameterValues(
                key="pipeline.charge_transfer.cdm.arguments.trap_densities",
                values=[[10, 20], [20, 30]],
            ),
        ]
    else:
        raise NotImplementedError


@pytest.fixture
def custom_parameter_values_lst() -> list[ParameterValues]:
    return [
        ParameterValues(
            key="pipeline.charge_transfer.cdm.arguments.beta",
            values="_",
        ),
        ParameterValues(
            key="pipeline.charge_transfer.cdm.arguments.trap_densities",
            values=["_", "_"],
        ),
    ]


@pytest.fixture
def simple_observation(
    product_parameter_values_lst: list[ParameterValues],
) -> Observation:
    return Observation(parameters=product_parameter_values_lst)


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
def processor(ccd_detector: CCD, pipeline: DetectionPipeline) -> Processor:
    return Processor(detector=ccd_detector, pipeline=pipeline)


@pytest.mark.parametrize(
    "result_type",
    [
        "scene",
        "photon",
        "charge",
        "pixel",
        "signal",
        "image",
        "data",
        "data.foo",
        "all",
    ],
)
def test_observation_product(
    product_parameter_values_lst: list[ParameterValues], result_type: str
):
    """Test method 'Observation.__init__' with 'product' mode."""
    observation = Observation(
        parameters=product_parameter_values_lst, mode="product", result_type=result_type
    )

    assert (
        repr(observation) == "Observation<mode=ParameterMode.Product, num_parameters=3>"
    )


@pytest.mark.parametrize(
    "result_type, exp_error, exp_msg",
    [
        ("foo", ValueError, r"Result type: 'foo' unknown"),
    ],
)
def test_observation_product_bad_inputs(
    product_parameter_values_lst: list[ParameterValues],
    result_type: str,
    exp_error: type[Exception],
    exp_msg: str,
):
    """Test method 'Observation.__init__' with 'product' mode and bad inputs."""
    with pytest.raises(exp_error, match=exp_msg):
        _ = Observation(
            parameters=product_parameter_values_lst,
            mode="product",
            result_type=result_type,
        )


@pytest.mark.parametrize(
    "result",
    [
        "scene",
        "photon",
        "charge",
        "pixel",
        "signal",
        "image",
        "data",
        "data.foo",
        "all",
    ],
)
def test_result_type(simple_observation: Observation, result: str):
    """Test property 'Observation.result_type'."""
    observation = simple_observation
    assert isinstance(observation, Observation)
    assert observation.result_type == "all"

    observation.result_type = result
    assert observation.result_type == result


@pytest.mark.parametrize("result", ["foo"])
def test_result_type_wrong_input(simple_observation: Observation, result: str):
    """Test property 'Observation.result_type' with wrong inputs."""
    observation = simple_observation
    assert isinstance(observation, Observation)

    with pytest.raises(ValueError, match="unknown"):
        observation.result_type = result


@pytest.mark.parametrize("seed", [0, 1234])
def test_pipeline_seed(simple_observation: Observation, seed: int):
    """Test property 'Observation.seed'."""
    observation = simple_observation
    assert isinstance(observation, Observation)
    assert observation.pipeline_seed is None

    observation.pipeline_seed = seed
    assert observation.pipeline_seed == seed


def test_enabled_steps(
    simple_observation: Observation,
    product_parameter_values_lst: list[ParameterValues],
):
    """Test method 'Observation.enabled_steps'."""
    observation = simple_observation
    assert isinstance(observation, Observation)

    values = observation.enabled_steps
    assert values == product_parameter_values_lst


def test_validate_steps(simple_observation: Observation, processor: Processor):
    """Test method 'Observation.validate_steps'."""
    observation = simple_observation
    assert isinstance(observation, Observation)

    observation.validate_steps(processor=processor)


@pytest.mark.parametrize("mode", ["product", "sequential"])
@pytest.mark.parametrize(
    "with_dask",
    [
        pytest.param(True, id="with dask"),
        pytest.param(False, id="without dask"),
    ],
)
@pytest.mark.parametrize(
    "with_outputs",
    [
        pytest.param(False, id="no outputs"),
        pytest.param(True, id="with outputs"),
    ],
)
def test_observation_datatree_no_custom(
    product_parameter_values_lst: list[ParameterValues],
    processor: Processor,
    tmp_path: Path,
    mode: str,
    with_dask: bool,
    with_outputs: bool,
):
    """Test method 'Observation.run_observation_datatree'."""
    if with_outputs is False:
        observation = Observation(
            parameters=product_parameter_values_lst,
            mode=mode,
            with_dask=with_dask,
        )
    else:
        observation = Observation(
            parameters=product_parameter_values_lst,
            mode=mode,
            with_dask=with_dask,
            outputs=ObservationOutputs(output_folder=tmp_path),
        )

    dt = observation._run_observation_datatree(processor, with_hiearchical_format=False)
    assert isinstance(dt, DataTree)


@pytest.mark.parametrize(
    "with_dask",
    [
        pytest.param(True, id="with dask"),
        pytest.param(False, id="without dask"),
    ],
)
@pytest.mark.parametrize(
    "with_outputs",
    [
        pytest.param(False, id="no outputs"),
        pytest.param(True, id="with outputs"),
    ],
)
def test_observation_datatree_with_custom(
    custom_parameter_values_lst: list[ParameterValues],
    processor: Processor,
    tmp_path: Path,
    with_dask: bool,
    with_outputs: bool,
):
    """Test method 'Observation.run_observation_datatree' with 'custom' mode."""
    folder = Path("tests/observation")

    if with_outputs is False:
        observation = Observation(
            parameters=custom_parameter_values_lst,
            from_file=folder / "data/densities.txt",
            column_range=(0, 3),
            mode="custom",
            with_dask=with_dask,
        )
    else:
        observation = Observation(
            parameters=custom_parameter_values_lst,
            mode="custom",
            from_file=folder / "data/densities.txt",
            column_range=(0, 3),
            with_dask=with_dask,
            outputs=ObservationOutputs(output_folder=tmp_path),
        )

    dt = observation._run_observation_datatree(processor, with_hiearchical_format=False)
    assert isinstance(dt, DataTree)
