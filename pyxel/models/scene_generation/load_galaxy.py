# Copyright (c) 2023 Alejandro Camazon Pinilla, University of Florida, ARRAKIHS Mission Consortium
#
# acamazon@ufl.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Load galaxy model."""
import warnings

warnings.filterwarnings("ignore")
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'
import pickle
from typing import Callable, Literal

import astropy.constants as cte
import astropy.units as u
import numpy as np
import xarray as xr

import pyxel.models.scene_generation.arrakihs_sph as sph
from pyxel.detectors import Detector


def galaxy_rot(X, Y, Z, alpha, beta, gamma):
    """
    A function for the rotation of Euler angles:

    Parameters
    -------
    X: 1-d array.
        Inital x-axis values.
    Y: 1-d array.
        Inital y-axis values.
    Z: 1-d array.
        Inital z-axis values.
    alpha: float (in degrees).
        Rotation angle along x-axis.
    beta: float (in degrees).
        Rotation angle along y-axis.
    gamma: float (in degrees).
        Rotation angle along z-axis.
    """
    # Transform degrees into radians
    alpha = np.deg2rad(alpha)
    beta = np.deg2rad(beta)
    gamma = np.deg2rad(gamma)

    # Compute the 3-d rotation matrix with Euler angles.
    x_rot = (
        X * (np.cos(alpha) * np.cos(beta))
        + Y
        * (
            -np.cos(gamma) * np.sin(alpha)
            + np.sin(gamma) * np.sin(beta) * np.cos(alpha)
        )
        + Z
        * (np.sin(gamma) * np.sin(alpha) + np.cos(gamma) * np.sin(beta) * np.cos(alpha))
    )
    y_rot = (
        X * (np.sin(alpha) * np.cos(beta))
        + Y
        * (np.cos(gamma) * np.cos(alpha) + np.sin(gamma) * np.sin(beta) * np.sin(alpha))
        + Z
        * (
            -np.sin(gamma) * np.cos(alpha)
            + np.cos(gamma) * np.sin(beta) * np.sin(alpha)
        )
    )
    z_rot = (
        -X * np.sin(beta)
        + Y * np.sin(gamma) * np.cos(beta)
        + Z * (np.cos(beta) * np.cos(gamma))
    )

    # Save results
    return x_rot, y_rot, z_rot


# CONSTANTS:

c_speed = cte.c  # light velocity in m/s
h_planck = 6.626075540e-34 * u.W * u.s**2  # Planck constant in W s


def garrotxa_model(galaxy_model: str = "0.750") -> pd.DataFrame:
    """A function that reads the GARROTXA Galaxies models:

    Parameters
    -------
    galaxy_model: str.
        Name of the model (Default value: "0.750". Options: "0.650", "0.750", "0.850", "1.000").
    """

    # Read the model selected
    print("########## Reading galaxy #########")
    dt = np.dtype(
        [
            ("Begining of the line", ">f"),
            ("rx", ">f"),
            ("ry", ">f"),
            ("rz", ">f"),
            ("VIS_flux", ">d"),
            ("J_flux", ">d"),
            ("Y_flux", ">d"),
            ("HSTF475X_flux", ">d"),
            ("End of the line", ">f"),
        ]
    )
    with open(
        "Files/Galaxy_models/GARROTXA/Stars_EUCLID_MW_a"
        + str(galaxy_model)
        + "_dist_indep.dat",
        "rb",
    ) as f:
        b = f.read()

    np_data = np.frombuffer(b, dt)
    file = pd.DataFrame(np_data.byteswap().newbyteorder())

    del file["Begining of the line"]
    del file["End of the line"]

    # Transforming coordinates units from Mpc/h to Mpc
    h_red = 0.6766  # Reduced Hubble's constant

    file["rx"] = file["rx"] * h_red
    file["ry"] = file["ry"] * h_red
    file["rz"] = file["rz"] * h_red

    return file


def dmf_model(galaxy_model="30keV"):
    """
        A function that reads the Dark Matter Flavours Galaxies models:

    Parameters
    -------
    galaxy_model: str.
        Name of the model (Default value: "30keV". Options: "1keV", "3keV", "10keV", "30keV").
    """

    # Read the model selected
    print("########## Reading galaxy #########")
    f = open(
        "Files/Galaxy_models/WDM_models/stars_" + str(galaxy_model) + "_1000kpc.pkl",
        "rb",
    )

    x = pickle.load(f)
    y = pickle.load(f)
    z = pickle.load(f)

    HSTF475Xmags = np.array(pickle.load(f)).astype("float64")
    VISmags = np.array(pickle.load(f)).astype("float64")
    Ymags = np.array(pickle.load(f)).astype("float64")
    Jmags = np.array(pickle.load(f)).astype("float64")

    print("Calculating Fluxes of stars")

    ######################
    ###### HST F475X filter
    ######################

    # Filter characteristics
    wave_begin_475X = (3735.11 * u.AA).to(u.m)
    wave_end_475X = (6919.31 * u.AA).to(u.m)
    wave_central_475X = (4852.88 * u.AA).to(u.m)

    energy_475X_phot = h_planck * c_speed / wave_central_475X

    # From AB Absolute Magnitude to Flux:
    HSTF475X_flux = 10 ** (-(HSTF475Xmags - 34.0947) / 2.5) * u.W / u.Hz
    # Integration factor in frecuancies:
    delta_nu = (
        c_speed
        * (wave_end_475X - wave_begin_475X)
        / (wave_begin_475X * wave_end_475X)
        * u.s
        * u.Hz
    )
    # Irradiance of the particles:
    HSTF475X_irrad = HSTF475X_flux * delta_nu
    # erg to photons:
    HSTF475X_phot = (HSTF475X_irrad / energy_475X_phot).to(1 / u.s).value

    ######################
    ###### VIS filter
    ######################

    # Filter characteristics
    wave_begin_vis = (537.5 * u.nm).to(u.m)
    wave_end_vis = (892.5 * u.nm).to(u.m)
    wave_central_vis = (715 * u.nm).to(u.m)

    energy_vis_phot = h_planck * c_speed / wave_central_vis

    # From AB Absolute Magnitude to Flux:
    VIS_flux = 10 ** (-(VISmags - 34.0947) / 2.5) * u.W / u.Hz
    # Integration factor in frecuancies:
    delta_nu = (
        c_speed
        * (wave_end_vis - wave_begin_vis)
        / (wave_begin_vis * wave_end_vis)
        * u.s
        * u.Hz
    )
    # Irradiance of the particles:
    VIS_irrad = VIS_flux * delta_nu
    # erg to photons:
    VIS_phot = (VIS_irrad / energy_vis_phot).to(1 / u.s).value

    ######################
    ###### Y filter
    ######################

    # Filter characteristics
    wave_begin_y = (947.5 * u.nm).to(u.m)
    wave_end_y = (1222.5 * u.nm).to(u.m)
    wave_central_y = (1085.0 * u.nm).to(u.m)

    energy_y_phot = h_planck * c_speed / wave_central_y

    # From AB Absolute Magnitude to Flux:
    Y_flux = 10 ** (-(Ymags - 34.0947) / 2.5) * u.W / u.Hz
    # Integration factor in frecuancies:
    delta_nu = (
        c_speed * (wave_end_y - wave_begin_y) / (wave_begin_y * wave_end_y) * u.s * u.Hz
    )
    # Irradiance of the particles:
    Y_irrad = Y_flux * delta_nu
    # erg to photons:
    Y_phot = (Y_irrad / energy_y_phot).to(1 / u.s).value

    ######################
    ###### J filter
    ######################

    # Filter characteristics
    wave_begin_j = (1160.0 * u.nm).to(u.m)
    wave_end_j = (1590.0 * u.nm).to(u.m)
    wave_central_j = (1375.0 * u.nm).to(u.m)

    energy_j_phot = h_planck * c_speed / wave_central_j

    # From AB Absolute Magnitude to Flux:
    J_flux = 10 ** (-(Jmags - 34.0947) / 2.5) * u.W / u.Hz
    # Integration factor in frecuancies:
    delta_nu = (
        c_speed * (wave_end_j - wave_begin_j) / (wave_begin_j * wave_end_j) * u.s * u.Hz
    )
    # Irradiance of the particles:
    J_irrad = J_flux * delta_nu
    # erg to photons:
    J_phot = (J_irrad / energy_j_phot).to(1 / u.s).value

    #############################
    ##### Printing data:
    #############################

    # We create new data with fluxes
    input_data = pd.DataFrame(data={"rx": x, "ry": y, "rz": z})
    input_data["HSTF475X_flux"] = HSTF475X_phot
    input_data["VIS_flux"] = VIS_phot
    input_data["Y_flux"] = Y_phot
    input_data["J_flux"] = J_phot

    file = input_data

    # Transforming coordinates units from kpc to Mpc

    file["rx"] = file["rx"] * 1e-3
    file["rx"] = file["rx"] - (np.max(file["rx"]) + np.min(file["rx"])) / 2
    file["ry"] = file["ry"] * 1e-3
    file["ry"] = file["ry"] - (np.max(file["ry"]) + np.min(file["ry"])) / 2
    file["rz"] = file["rz"] * 1e-3
    file["rz"] = file["rz"] - (np.max(file["rz"]) + np.min(file["rz"])) / 2

    return file


def coco_model(galaxy_model="98767_153"):
    """
        A function that reads the CoCo Galaxies models:

    Parameters
    -------
    galaxy_model: str.
        Name of the model (Default value: "98767_153". Options: "98767_153").
    """
    # Read the model selected
    print("########## Reading galaxy #########")
    dt = np.dtype(
        [
            ("Begining of the line", ">f"),
            ("rx", ">f"),
            ("ry", ">f"),
            ("rz", ">f"),
            ("VIS_flux", ">d"),
            ("J_flux", ">d"),
            ("Y_flux", ">d"),
            ("HSTF475X_flux", ">d"),
            ("hsml", ">d"),
            ("End of the line", ">f"),
        ]
    )
    with open(
        "/Volumes/disk5/Arrakihs_1/image_forming/Gal_data/CoCo_subhalo_"
        + str(galaxy_model)
        + "_dist_indep.dat",
        "rb",
    ) as f:
        b = f.read()

    np_data = np.frombuffer(b, dt)
    file = pd.DataFrame(np_data.byteswap().newbyteorder())

    del file["Begining of the line"]
    del file["End of the line"]

    # Transforming coordinates units from Mpc/h to Mpc
    h_red = 0.6766  # Reduced Hubble's constant

    file["rx"] = file["rx"] * h_red
    file["ry"] = file["ry"] * h_red
    file["rz"] = file["rz"] * h_red

    return file


def model_creator(
    cosmo_model: Callable = dmf_model,
    galaxy_model: str = "30keV",
    dist: float = 25.0,
    plate_scale: float = 1.675,
    s_size: int = 3400,
    angles: np.ndarray = np.array([0.0, 0.0, 0.0]),
    band_var: str = "Euclid_VIS",
    n_neighbors: int = 8,
) -> np.ndarray:
    """
        A function that creates the smooth image from the galaxies models for the ARRAKIHS filters.

    Parameters
    -------
    cosmo_model: function.
        Name of the cosmological model function (Default value: dmf_model (Dark Matter Flavours). Options: garrotxa_model, dmf_model, coco_model).
    galaxy_model: str.
        Name of the model (Default value: "30keV". Options depends on the cosmological model selected:
                            - DMF model: "1keV", "3keV", "10keV", "30keV"
                            - GARROTXA model: "0.650", "0.750", "0.850", "1.000"
                            - CoCo model: "98767_153").
    dist: float (in Mpc).
        Physical distance to place the galaxy model (Default: 25.0 Mpc).
    plate_scale: float (in arcsec/pixel).
        Plate scale of the telescope+detector used (Default: 1.675 arcsec/pixel).
    s_size: int (in number of pixels).
        Number of pixels of the detector (Default: 3400).
    angles: 1-d float numpy array (in degrees).
        Euler's rotation angles to rotate the initial postion of the galaxy model (Default: alpha=0.0, beta=0.0, gamma=0.0).
    band_var: str.
        Filter used in the simulation (Default: "Euclid_VIS". Options: "HST_F475X", "Euclid_VIS", "Euclid_Y", "Euclid_J").
    n_neighbors: int.
        Number of nearest neighbors used to calculate the adaptative kernel to smooth the galaxy model (Default: 8).
    """

    # read the file from the corresponding galaxy model:
    file = cosmo_model(galaxy_model)

    # calculate the hsml in case it has not been already provided:
    if "hsml" in file:
        pass
    else:
        n_neighbors = n_neighbors

        print("Finding ", n_neighbors, " Nearest Neighbors")
        xyz = np.transpose(np.array([file["rx"], file["ry"], file["rz"]]))
        hsml = sph.get_smoothing_lengths(xyz, ngb=n_neighbors)
        file["hsml"] = hsml

    # we create a bigger image in case the center of the galaxy is not centered in the image
    size_ampl = s_size + 2500

    mpc_pixel = dist * (
        plate_scale / 206265
    )  # Mpc/pixel for a certain distance and plate scale
    upper_limit = (size_ampl / 2) * mpc_pixel  # Maximum Mpc position inside the image
    lower_limit = -(size_ampl / 2) * mpc_pixel  # Minimum Mpc position inside the image

    alpha = angles[0]  # Angle rotation x axis
    beta = angles[1]  # Angle rotation y axis
    gamma = angles[2]  # Angle rotation z axis

    # we apply the rotation matrix
    position = galaxy_rot(file["rx"], file["ry"], file["rz"], alpha, beta, gamma)

    # Redifine the new positions:
    file["X_rot"] = position[0]
    file["Y_rot"] = position[1]
    file["Z_rot"] = position[2]

    # We create a new table with rotated positions and limitted by the maximum and minimum values inside the image:
    df_new = (
        file[
            (file["X_rot"] >= lower_limit)
            & (file["X_rot"] <= upper_limit)
            & (file["Y_rot"] >= lower_limit)
            & (file["Y_rot"] <= upper_limit)
        ]
    ).reset_index(drop=True)
    new_xyz = np.transpose(
        np.array([df_new["Y_rot"], df_new["X_rot"], df_new["Z_rot"]])
    )

    length_x = np.round(
        (new_xyz[:][:, 0]).max() - (new_xyz[:][:, 0]).min(), 2
    )  # total size in x-axis in Mpc
    length_y = np.round(
        (new_xyz[:][:, 1]).max() - (new_xyz[:][:, 1]).min(), 2
    )  # total size in y-axis in Mpc
    length_z = np.round(
        (new_xyz[:][:, 2]).max() - (new_xyz[:][:, 2]).min(), 2
    )  # total size in z-axis in Mpc

    len_grid_scaled_x = int(
        round(length_x / mpc_pixel, 1)
    )  # total size in x-axis in number of pixels
    len_grid_scaled_y = int(
        round(length_y / mpc_pixel, 1)
    )  # total size in x-axis in number of pixels
    len_grid_scaled_z = int(
        round(length_z / mpc_pixel, 1)
    )  # total size in x-axis in number of pixels

    # we set a grid with the number of pixels we will project the galaxy
    grid_x, grid_y = np.arange(
        -len_grid_scaled_x / 2, len_grid_scaled_x / 2
    ), np.arange(-len_grid_scaled_y / 2, len_grid_scaled_y / 2)
    # We calculate the photon irradiance for the given distance.
    if band_var == "HST_F475X":
        print("########## HST F475X model #########")
        irradiance_photons = df_new["HSTF475X_flux"].values / (
            4 * np.pi * ((dist * u.Mpc).to(u.cm)) ** 2
        )

    if band_var == "Euclid_VIS":
        print("########## Euclid-VIS model #########")
        irradiance_photons = df_new["VIS_flux"].values / (
            4 * np.pi * ((dist * u.Mpc).to(u.cm)) ** 2
        )

    if band_var == "Euclid_Y":
        print("########## Euclid-Y model #########")
        irradiance_photons = df_new["Y_flux"].values / (
            4 * np.pi * ((dist * u.Mpc).to(u.cm)) ** 2
        )

    if band_var == "Euclid_J":
        print("########## Euclid-J model #########")
        irradiance_photons = df_new["J_flux"].values / (
            4 * np.pi * ((dist * u.Mpc).to(u.cm)) ** 2
        )

    # we create the smooth image of the model
    model_smooth = (
        sph.example_usage(
            xyz=new_xyz,
            mass=irradiance_photons,
            gridx=grid_x,
            gridy=grid_y,
            hsml=df_new["hsml"].values,
            proj=2,
        )
        * mpc_pixel**2
    )

    # The physical size of the galaxy model must be of the same size of the detector size. In case it is not, the size of the image won't be the same as the selected size:
    if model_smooth.shape != (size_ampl, size_ampl):
        pixels_need_y = (
            size_ampl - len_grid_scaled_x
        )  # number of pixels needed in y-axis:
        pixels_need_y_1st_half = int(
            pixels_need_y / 2
        )  # number of pixels needed in y-axis in each side of the image
        pixels_need_y_2nd_half = int(pixels_need_y - pixels_need_y_1st_half)

        add_y_1 = np.zeros(
            [pixels_need_y_1st_half, len_grid_scaled_y]
        )  # array of zeros that must be added in each side along y-axis
        add_y_2 = np.zeros([pixels_need_y_2nd_half, len_grid_scaled_y])

        pixels_need_x = (
            size_ampl - len_grid_scaled_y
        )  # number of pixels needed in x-axis:
        pixels_need_x_1st_half = int(
            pixels_need_x / 2
        )  # number of pixels needed in x-axis in each side of the image
        pixels_need_x_2nd_half = int(pixels_need_x - pixels_need_x_1st_half)

        add_x_1 = np.zeros(
            [size_ampl, pixels_need_x_1st_half]
        )  # array of zeros that must be added in each side along x-axis
        add_x_2 = np.zeros([size_ampl, pixels_need_x_2nd_half])

        new_image_1 = np.concatenate(
            (add_y_1, model_smooth), axis=0
        )  # additional y-axis array
        new_image_2 = np.concatenate(
            (new_image_1, add_y_2), axis=0
        )  # additional y-axis array
        new_image_3 = np.concatenate(
            (add_x_1, new_image_2), axis=1
        )  # additional x-axis array
        model_smooth = np.concatenate(
            (new_image_3, add_x_2), axis=1
        )  # additional x-axis array

    # We make sure that the center of the galaxy is placed in the center of the image:
    true_image = np.zeros([s_size, s_size])
    # We look for the center of the galaxy (maximum value of the flux)
    index_center_y, index_center_x = np.where(model_smooth == np.max(model_smooth))
    # we wrap the image around the maximum
    model_smooth_center = model_smooth[
        int(index_center_y[0] - true_image.shape[0] / 2) : int(
            index_center_y[0] + true_image.shape[0] / 2
        ),
        int(index_center_x[0] - true_image.shape[0] / 2) : int(
            index_center_x[0] + true_image.shape[0] / 2
        ),
    ]
    new_shape = model_smooth_center.shape
    true_image[: new_shape[0], : new_shape[1]] = model_smooth_center

    return true_image


def load_galaxy(
    detector: Detector,
    cosmo_model: Literal["dmf_model", "coco_model", "garrotxa_model"] = "dmf_model",
    galaxy_model: str = "30keV",
    dist: float = 25.0,
    plate_scale: float = 1.65,
    s_size: int = 3400,
    angles: np.ndarray = np.array([0.0, 0.0, 0.0]),
    band_var: str = "Euclid_VIS",
    n_neighbors: int = 8,
) -> None:
    if cosmo_model == "dmf_model":
        cosmo_model_func: Callable = dmf_model
    else:
        raise NotImplementedError

    scene_2d: np.ndarray = model_creator(
        cosmo_model=cosmo_model_func,
        galaxy_model=galaxy_model,
        dist=dist,
        plate_scale=plate_scale,
        s_size=s_size,
        angles=angles,
        band_var=band_var,
        n_neighbors=n_neighbors,
    )

    detector.data["/scene"] = xr.DataArray(scene_2d, attrs={"units": "photon/s/cm2"})
