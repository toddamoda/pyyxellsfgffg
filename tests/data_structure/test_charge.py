#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from pyxel.data_structure import Charge
from pyxel.detectors import Geometry


@pytest.fixture
def geo() -> Geometry:
    return Geometry(
        row=4,
        col=5,
        total_thickness=10.0,
        pixel_horz_size=1.0,
        pixel_vert_size=1.0,
    )


def test_empty_charge(geo: Geometry):
    """Test an empty `Charge` object."""
    charge = Charge(geo=geo)

    assert charge.nextid == 0

    pd.testing.assert_frame_equal(
        charge.frame,
        pd.DataFrame(
            data=None,
            columns=(
                "charge",
                "number",
                "init_energy",
                "energy",
                "init_pos_ver",
                "init_pos_hor",
                "init_pos_z",
                "position_ver",
                "position_hor",
                "position_z",
                "velocity_ver",
                "velocity_hor",
                "velocity_z",
            ),
            dtype=float,
        ),
    )


def test_add_one_charge(geo: Geometry):
    """Test with one charge."""
    charge = Charge(geo=geo)

    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1]),
        init_energy=np.array([0.1]),
        init_ver_position=np.array([1.1]),
        init_hor_position=np.array([2.2]),
        init_z_position=np.array([3.3]),
        init_ver_velocity=np.array([4.4]),
        init_hor_velocity=np.array([-5.5]),
        init_z_velocity=np.array([6.6]),
    )

    exp_df_charges = pd.DataFrame(
        {
            "charge": np.array([-1]),
            "number": np.array([1]),
            "init_energy": np.array([0.1]),
            "energy": np.array([0.1]),
            "init_pos_ver": np.array([1.1]),
            "init_pos_hor": np.array([2.2]),
            "init_pos_z": np.array([3.3]),
            "position_ver": np.array([1.1]),
            "position_hor": np.array([2.2]),
            "position_z": np.array([3.3]),
            "velocity_ver": np.array([4.4]),
            "velocity_hor": np.array([-5.5]),
            "velocity_z": np.array([6.6]),
        }
    )

    # ensure that the integer types are consistent
    exp_df_charges["charge"] = exp_df_charges["charge"].astype(np.int64)
    exp_df_charges["number"] = exp_df_charges["number"].astype(np.int64)
    charge.frame["charge"] = charge.frame["charge"].astype(np.int64)
    charge.frame["number"] = charge.frame["number"].astype(np.int64)

    assert charge.nextid == 1
    pd.testing.assert_frame_equal(charge.frame, exp_df_charges)


def test_eq(geo: Geometry):
    """Test method 'Charge.__eq__'."""
    charge1 = Charge(geo)
    charge2 = Charge(geo)
    assert charge1 == charge2

    # Add particles to 'charge1'
    charge1.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1]),
        init_energy=np.array([0.1]),
        init_ver_position=np.array([1.1]),
        init_hor_position=np.array([2.2]),
        init_z_position=np.array([3.3]),
        init_ver_velocity=np.array([4.4]),
        init_hor_velocity=np.array([-5.5]),
        init_z_velocity=np.array([6.6]),
    )
    assert charge1 != charge2

    # Add same particles to 'charge2'
    charge2.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1]),
        init_energy=np.array([0.1]),
        init_ver_position=np.array([1.1]),
        init_hor_position=np.array([2.2]),
        init_z_position=np.array([3.3]),
        init_ver_velocity=np.array([4.4]),
        init_hor_velocity=np.array([-5.5]),
        init_z_velocity=np.array([6.6]),
    )
    assert charge1 == charge2

    # Add different particles to 'charge3'
    charge3 = Charge(geo)
    charge3.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([2]),
        init_energy=np.array([0.1]),
        init_ver_position=np.array([1.1]),
        init_hor_position=np.array([2.2]),
        init_z_position=np.array([3.3]),
        init_ver_velocity=np.array([4.4]),
        init_hor_velocity=np.array([-5.5]),
        init_z_velocity=np.array([6.6]),
    )
    assert charge1 != charge3


def test_add_one_hole(geo: Geometry):
    """Test with one hole."""
    charge = Charge(geo=geo)

    charge.add_charge(
        particle_type="h",
        particles_per_cluster=np.array([1]),
        init_energy=np.array([0.1]),
        init_ver_position=np.array([1.1]),
        init_hor_position=np.array([2.2]),
        init_z_position=np.array([3.3]),
        init_ver_velocity=np.array([4.4]),
        init_hor_velocity=np.array([-5.5]),
        init_z_velocity=np.array([6.6]),
    )

    exp_df_charges = pd.DataFrame(
        {
            "charge": [1],
            "number": [1],
            "init_energy": [0.1],
            "energy": [0.1],
            "init_pos_ver": [1.1],
            "init_pos_hor": [2.2],
            "init_pos_z": [3.3],
            "position_ver": [1.1],
            "position_hor": [2.2],
            "position_z": [3.3],
            "velocity_ver": [4.4],
            "velocity_hor": [-5.5],
            "velocity_z": [6.6],
        }
    )

    # ensure that the integer types are consistent
    exp_df_charges["charge"] = exp_df_charges["charge"].astype(np.int64)
    exp_df_charges["number"] = exp_df_charges["number"].astype(np.int64)
    charge.frame["charge"] = charge.frame["charge"].astype(np.int64)
    charge.frame["number"] = charge.frame["number"].astype(np.int64)

    assert charge.nextid == 1
    pd.testing.assert_frame_equal(charge.frame, exp_df_charges)


@dataclass
class ChargeInfo:
    """Define one charge.

    Only for testing.
    """

    particle_type: Literal["e", "h"]
    particles_per_cluster: np.ndarray
    init_energy: np.ndarray
    init_ver_position: np.ndarray
    init_hor_position: np.ndarray
    init_z_position: np.ndarray
    init_ver_velocity: np.ndarray
    init_hor_velocity: np.ndarray
    init_z_velocity: np.ndarray


@pytest.mark.parametrize(
    "param_name",
    [
        "particles_per_cluster",
        "init_energy",
        "init_ver_position",
        "init_hor_position",
        "init_z_position",
        "init_ver_velocity",
        "init_hor_velocity",
        "init_z_velocity",
    ],
)
@pytest.mark.parametrize(
    "new_value, exp_error",
    [
        pytest.param(
            np.array([]),
            r"List arguments have different lengths",
            id="Too few values",
        ),
        pytest.param(
            np.array([1.0, 2.0]),
            r"List arguments have different lengths",
            id="Too much values",
        ),
        pytest.param(
            np.array([[1.0]]),
            r"List arguments must have only one dimension",
            id="More than one dimension",
        ),
    ],
)
def test_invalid_add_charge(param_name: str, geo: Geometry, new_value, exp_error):
    """Test method `Charge.add_charge` with invalid parameters."""
    charge = Charge(geo=geo)

    # Create valid parameters
    params = ChargeInfo(
        particle_type="e",
        particles_per_cluster=np.array([1]),
        init_energy=np.array([0.1]),
        init_ver_position=np.array([1.1]),
        init_hor_position=np.array([2.2]),
        init_z_position=np.array([3.3]),
        init_ver_velocity=np.array([4.4]),
        init_hor_velocity=np.array([-5.5]),
        init_z_velocity=np.array([6.6]),
    )

    # Add the valid parameters
    charge.add_charge(
        particle_type=params.particle_type,
        particles_per_cluster=params.particles_per_cluster,
        init_energy=params.init_energy,
        init_ver_position=params.init_ver_position,
        init_hor_position=params.init_hor_position,
        init_z_position=params.init_z_position,
        init_ver_velocity=params.init_ver_velocity,
        init_hor_velocity=params.init_hor_velocity,
        init_z_velocity=params.init_z_velocity,
    )

    # Add an invalid parameter
    # This is equivalent to 'params.param_name = new_value'
    setattr(params, param_name, new_value)

    with pytest.raises(ValueError, match=exp_error):
        charge.add_charge(
            particle_type=params.particle_type,
            particles_per_cluster=params.particles_per_cluster,
            init_energy=params.init_energy,
            init_ver_position=params.init_ver_position,
            init_hor_position=params.init_hor_position,
            init_z_position=params.init_z_position,
            init_ver_velocity=params.init_ver_velocity,
            init_hor_velocity=params.init_hor_velocity,
            init_z_velocity=params.init_z_velocity,
        )


@pytest.mark.parametrize("particle_type", ["E", "H", "electron", "hole"])
def test_invalid_particle_type(geo: Geometry, particle_type: Literal["e", "h"]):
    """Test method `Charge.add_charge` with invalid 'particle_type."""
    charge = Charge(geo=geo)

    with pytest.raises(
        ValueError, match="Given charged particle type can not be simulated"
    ):
        charge.add_charge(
            particle_type=particle_type,
            particles_per_cluster=np.array([1]),
            init_energy=np.array([0.1]),
            init_ver_position=np.array([1.1]),
            init_hor_position=np.array([2.2]),
            init_z_position=np.array([3.3]),
            init_ver_velocity=np.array([4.4]),
            init_hor_velocity=np.array([-5.5]),
            init_z_velocity=np.array([6.6]),
        )


def test_add_two_charges(geo: Geometry):
    """Test when adding one charges in one time."""
    charge = Charge(geo=geo)

    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    exp_df_charges = pd.DataFrame(
        {
            "charge": [-1, -1],
            "number": [1, 2],
            "init_energy": [0.1, 0.2],
            "energy": [0.1, 0.2],
            "init_pos_ver": [1.11, 1.12],
            "init_pos_hor": [2.21, 2.22],
            "init_pos_z": [3.31, 3.32],
            "position_ver": [1.11, 1.12],
            "position_hor": [2.21, 2.22],
            "position_z": [3.31, 3.32],
            "velocity_ver": [4.41, 4.42],
            "velocity_hor": [-5.51, 5.52],
            "velocity_z": [6.61, 6.62],
        }
    )

    # ensure that the integer types are consistent
    exp_df_charges["charge"] = exp_df_charges["charge"].astype(np.int64)
    exp_df_charges["number"] = exp_df_charges["number"].astype(np.int64)
    charge.frame["charge"] = charge.frame["charge"].astype(np.int64)
    charge.frame["number"] = charge.frame["number"].astype(np.int64)

    assert charge.nextid == 2
    pd.testing.assert_frame_equal(charge.frame, exp_df_charges)


def test_add_two_charges_one_hole(geo: Geometry):
    """Test when adding two charges and then one hole."""
    charge = Charge(geo=geo)

    # Add 2 charges
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    # Add 1 hole
    charge.add_charge(
        particle_type="h",
        particles_per_cluster=np.array([3]),
        init_energy=np.array([0.3]),
        init_ver_position=np.array([1.13]),
        init_hor_position=np.array([2.23]),
        init_z_position=np.array([3.33]),
        init_ver_velocity=np.array([4.43]),
        init_hor_velocity=np.array([5.53]),
        init_z_velocity=np.array([6.63]),
    )

    exp_df_charges = pd.DataFrame(
        {
            "charge": [-1, -1, 1],
            "number": [1, 2, 3],
            "init_energy": [0.1, 0.2, 0.3],
            "energy": [0.1, 0.2, 0.3],
            "init_pos_ver": [1.11, 1.12, 1.13],
            "init_pos_hor": [2.21, 2.22, 2.23],
            "init_pos_z": [3.31, 3.32, 3.33],
            "position_ver": [1.11, 1.12, 1.13],
            "position_hor": [2.21, 2.22, 2.23],
            "position_z": [3.31, 3.32, 3.33],
            "velocity_ver": [4.41, 4.42, 4.43],
            "velocity_hor": [-5.51, 5.52, 5.53],
            "velocity_z": [6.61, 6.62, 6.63],
        }
    )

    # ensure that the integer types are consistent
    exp_df_charges["charge"] = exp_df_charges["charge"].astype(np.int64)
    exp_df_charges["number"] = exp_df_charges["number"].astype(np.int64)
    charge.frame["charge"] = charge.frame["charge"].astype(np.int64)
    charge.frame["number"] = charge.frame["number"].astype(np.int64)

    assert charge.nextid == 3
    pd.testing.assert_frame_equal(charge.frame, exp_df_charges)


def test_add_charge_array_empty(geo: Geometry):
    """Test method 'Charge.add_charge_array'."""
    # No charges
    charge = Charge(geo=geo)

    data_2d = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    charge.add_charge_array(array=data_2d)


def test_add_charge_array_not_empty(geo: Geometry):
    """Test method 'Charge.add_charge_array'."""
    charge = Charge(geo=geo)
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    data_2d = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    charge.add_charge_array(array=data_2d)


def test_array(geo: Geometry):
    """Test property 'Charge.array'."""
    data_2d = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )

    charge = Charge(geo=geo)
    charge.add_charge_array(array=data_2d.copy())

    value = charge.array
    assert isinstance(value, np.ndarray)
    np.testing.assert_allclose(data_2d, value)


@pytest.mark.parametrize(
    "array, exp_error, exp_msg",
    [
        (
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 3.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ],
            TypeError,
            r"Charge array should be a numpy.ndarray",
        ),
        (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 3, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                ],
                dtype=int,
            ),
            TypeError,
            r"Expected type of Charge array is ",
        ),
        (
            np.array(
                [
                    [0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 3.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0],
                ],
                dtype=float,
            ),
            ValueError,
            r"Expected Charge array is \(4, 5\)",
        ),
    ],
)
def test_array_wrong_input(geo: Geometry, array, exp_error, exp_msg):
    """Test property 'Charge.array'."""
    charge = Charge(geo=geo)

    with pytest.raises(exp_error, match=exp_msg):
        charge.add_charge_array(array=array)


def test_array_with_df(geo: Geometry):
    """Test property 'Charge.array'."""
    charge = Charge(geo=geo)
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    value = charge.array
    assert isinstance(value, np.ndarray)

    exp_value = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    np.testing.assert_allclose(value, exp_value)


def test_to_xarray(geo: Geometry):
    """Test method 'Charge.to_xarray'."""
    charge = Charge(geo=geo)
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    data_array = charge.to_xarray()
    assert isinstance(data_array, xr.DataArray)

    exp_data_array = xr.DataArray(
        np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 3.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ],
            dtype=float,
        ),
        dims=["y", "x"],
        coords={"y": [0, 1, 2, 3], "x": [0, 1, 2, 3, 4]},
        attrs={"units": "e⁻", "long_name": "Charge"},
    )
    xr.testing.assert_equal(data_array, exp_data_array)


def test__array__(geo: Geometry):
    """Test method 'Charge.__array__'."""
    data_2d = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )

    charge = Charge(geo=geo)
    charge.add_charge_array(data_2d.copy())

    value = np.array(charge)
    np.testing.assert_equal(value, data_2d)


def test_frame(geo: Geometry):
    """Test property 'Charge.frame'."""
    charge = Charge(geo=geo)
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    df = charge.frame
    assert isinstance(df, pd.DataFrame)


def test_empty(geo: Geometry):
    """Test method 'Charge.empty'."""
    charge = Charge(geo=geo)
    assert charge.frame_empty() is True

    # Add charges
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )
    assert charge.frame_empty() is False

    # Remove everything
    charge.empty()
    assert charge.frame_empty() is True


def test_convert_df_to_array(geo: Geometry):
    """Test method 'Charge.convert_df_to_array."""
    charge = Charge(geo=geo)

    # Add 2 charges
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    # Test 'Charge.convert_df_to_array'
    result_2d = charge.convert_df_to_array()
    assert isinstance(result_2d, np.ndarray)

    exp_2d = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    np.testing.assert_allclose(result_2d, exp_2d)


def test_convert_array_to_df(geo: Geometry):
    """Test method 'Charge.convert_array_to_df'."""
    data_2d = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )

    df = Charge.convert_array_to_df(
        array=data_2d,
        num_rows=geo.row,
        num_cols=geo.col,
        pixel_vertical_size=geo.pixel_vert_size,
        pixel_horizontal_size=geo.pixel_horz_size,
    )
    assert isinstance(df, pd.DataFrame)


def test_invalid_add_charge_dataframe(geo: Geometry):
    """Test method `Charge.add_charge_dataframe` with an invalid input."""
    charge = Charge(geo=geo)

    df = pd.DataFrame(
        {
            "charge": [1.0],
            "number": [1.0],
            "init_energy": [0.1],
            "energy": [0.1],
            "init_pos_ver": [1.1],
            "init_pos_hor": [2.2],
            "init_pos_z": [3.3],
            "position_ver": [1.1],
            "position_hor": [2.2],
            "position_z": [3.3],
            "BAD_COLUMN": [4.4],  # Wrong column
            "velocity_hor": [-5.5],
            "velocity_z": [6.6],
        }
    )

    with pytest.raises(
        ValueError,
        match=r"Expected columns: 'charge', 'number', 'init_energy', 'energy', "
        r"'init_pos_ver', 'init_pos_hor', 'init_pos_z', "
        r"'position_ver', 'position_hor', 'position_z', "
        r"'velocity_ver', 'velocity_hor', 'velocity_z'",
    ):
        charge.add_charge_dataframe(new_charges=df)


def test_get_frame_values(geo: Geometry):
    """Test method 'Charge.get_frame_values'."""
    charge = Charge(geo=geo)

    # Add 2 charges
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    value = charge.get_frame_values(quantity="charge")
    np.testing.assert_equal(value, np.array([-1, -1]))

    value = charge.get_frame_values(quantity="energy")
    np.testing.assert_equal(value, np.array([0.1, 0.2]))


def test_set_frame_values(geo: Geometry):
    """Test method 'Charge.set_frame_values'."""
    charge = Charge(geo=geo)

    # Add 2 charges
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    charge.set_frame_values(quantity="energy", new_value_list=[1.1, 1.2])

    value = charge.get_frame_values(quantity="energy")
    np.testing.assert_equal(value, np.array([1.1, 1.2]))


def test_remove_from_frame(geo: Geometry):
    """Test method 'Charge.remove_from_frame'."""
    charge = Charge(geo=geo)

    # Add 2 charges
    charge.add_charge(
        particle_type="e",
        particles_per_cluster=np.array([1, 2]),
        init_energy=np.array([0.1, 0.2]),
        init_ver_position=np.array([1.11, 1.12]),
        init_hor_position=np.array([2.21, 2.22]),
        init_z_position=np.array([3.31, 3.32]),
        init_ver_velocity=np.array([4.41, 4.42]),
        init_hor_velocity=np.array([-5.51, 5.52]),
        init_z_velocity=np.array([6.61, 6.62]),
    )

    charge.remove_from_frame(id_list=[0])

    value = charge.get_frame_values(quantity="energy")
    np.testing.assert_equal(value, np.array([0.2]))
