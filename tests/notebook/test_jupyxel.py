#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr

from pyxel.configuration import Configuration
from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.exposure import Exposure, Readout
from pyxel.notebook import (
    change_modelparam,
    display_array,
    display_config,
    display_detector,
    display_model,
    display_scene,
)
from pyxel.notebook.jupyxel import set_modelstate
from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor


@pytest.fixture
def ccd_detector() -> CCD:
    detector = CCD(
        geometry=CCDGeometry(row=2, col=3, pixel_scale=0.1),
        environment=Environment(temperature=238.0),
        characteristics=Characteristics(full_well_capacity=90_0000),
    )

    return detector


@pytest.fixture
def detection_pipeline() -> DetectionPipeline:
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
def processor(ccd_detector: CCD, detection_pipeline: DetectionPipeline) -> Processor:
    return Processor(detector=ccd_detector, pipeline=detection_pipeline)


@pytest.fixture
def configuration(
    ccd_detector: CCD, detection_pipeline: DetectionPipeline
) -> Configuration:
    return Configuration(
        ccd_detector=ccd_detector,
        exposure=Exposure(readout=Readout()),
        pipeline=detection_pipeline,
    )


@pytest.mark.parametrize("name", ["all", "exposure", "unknown"])
def test_display_config(configuration: Configuration, name: str):
    """Test function 'display_config'."""
    display_config(configuration=configuration, only=name)


def test_display_model(configuration: Configuration):
    """Test function 'display_model'."""
    display_model(configuration=configuration, model_name="cdm")


def test_display_model_wrong_input(configuration: Configuration):
    """Test function 'display_model' with wrong input."""
    with pytest.raises(AttributeError, match="Model has not been found"):
        display_model(configuration=configuration, model_name="unknown")


def test_change_modelparam(processor: Processor):
    """Test function 'change_modelparam'."""
    change_modelparam(
        processor=processor, model_name="cdm", argument="beta", changed_value=4.0
    )


@pytest.mark.parametrize(
    "model_name, argument, changed_value, exp_exc, exp_err",
    [
        ("unknown", "beta", 4.0, AttributeError, "Model has not been found"),
        ("cdm", "unknown", 4.0, KeyError, "No argument named unknown"),
    ],
)
def test_change_modelparam_wrong_inputs(
    processor: Processor,
    model_name: str,
    argument: str,
    changed_value: Any,
    exp_exc: type[Exception],
    exp_err: str,
):
    """Test function 'change_modelparam' with wrong inputs."""
    with pytest.raises(exp_exc, match=exp_err):
        change_modelparam(
            processor=processor,
            model_name=model_name,
            argument=argument,
            changed_value=changed_value,
        )


@pytest.mark.parametrize("state", [True, False])
def test_set_modelstate(processor: Processor, state: bool):
    """Test function 'set_modelstate'."""
    set_modelstate(processor=processor, model_name="cdm", state=state)


def test_set_modelstate_wrong_input(processor: Processor):
    """Test function 'set_modelstate' with wrong inputs."""
    with pytest.raises(AttributeError, match="Model has not been found"):
        set_modelstate(processor=processor, model_name="unknown")


@pytest.mark.parametrize("new_display", [True, False, None])
@pytest.mark.parametrize("custom_histogram", [True, False, None])
def test_display_detector(
    ccd_detector: CCD, new_display: bool | None, custom_histogram: bool | None
):
    """Test function 'display_detector'."""
    ccd_detector.photon.array = np.zeros(shape=(2, 3))

    if new_display is None:
        if custom_histogram is None:
            _ = display_detector(detector=ccd_detector)
        else:
            _ = display_detector(
                detector=ccd_detector,
                custom_histogram=custom_histogram,
            )
    else:
        if custom_histogram is None:
            _ = display_detector(
                detector=ccd_detector,
                new_display=new_display,
            )
        else:
            _ = display_detector(
                detector=ccd_detector,
                new_display=new_display,
                custom_histogram=custom_histogram,
            )


def test_display_detector_no_arrays(ccd_detector: CCD):
    """Test function 'display_detector' no arrays."""
    with pytest.raises(ValueError, match="Detector object does not contain any arrays"):
        _ = display_detector(detector=ccd_detector)


def test_display_scene(ccd_detector: CCD):
    """Test function 'display_scene'."""
    source = xr.Dataset(
        {
            "x": xr.DataArray([64.97, 11.94, -55.75, -20.66], dims="ref"),
            "y": xr.DataArray([89.62, -129.3, -48.16, 87.87], dims="ref"),
            "weight": xr.DataArray([14.73, 12.34, 14.63, 14.27], dims="ref"),
            "flux": xr.DataArray(
                [
                    [0.1, 0.2, 0.3, 0.4],
                    [0.5, 0.6, 0.7, 0.8],
                    [0.9, 1.0, 1.1, 1.2],
                    [1.3, 1.4, 1.5, 1.6],
                ],
                dims=["ref", "wavelength"],
            ),
        },
        coords={"ref": [0, 1, 2, 3], "wavelength": [336.0, 338.0, 1018.0, 1020.0]},
        attrs={
            "right_ascension": "57.1829668 deg",
            "declination": "23.84371349 deg",
            "fov_radius": "0.5 deg",
        },
    )

    ccd_detector.scene.add_source(source)
    display_scene(detector=ccd_detector)


def test_display_array():
    """Test function 'display_array'."""
    data_2d = np.arange(5 * 5, dtype=float).reshape(5, 5)

    _, (ax1, ax2) = plt.subplots(nrows=2)
    display_array(data=data_2d, axes=(ax1, ax2), label="my_label")


def test_display_array2():
    """Test function 'display_array'."""
    data_2d = np.full(shape=(5, 5), fill_value=1.0, dtype=float)

    _, (ax1, ax2) = plt.subplots(nrows=2)
    display_array(data=data_2d, axes=(ax1, ax2), label="my_label")


def test_display_array_missing_label():
    """Test function 'display_array' without parameter 'label'."""
    data_2d = np.arange(5 * 5, dtype=float).reshape(5, 5)

    _, (ax1, ax2) = plt.subplots(nrows=2)

    with pytest.raises(KeyError, match=r"'label'"):
        display_array(data=data_2d, axes=(ax1, ax2))
