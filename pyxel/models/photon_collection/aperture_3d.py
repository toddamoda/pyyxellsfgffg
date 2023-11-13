#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Convert scene to 3D photon with aperture model."""

import astropy.units as u
import numpy as np
import xarray as xr
from astropy import wcs
from astropy.coordinates import SkyCoord

from pyxel.data_structure import Photon3D
from pyxel.detectors import Detector
from pyxel.models.photon_collection.aperture import convert_flux


def project_objects_to_detector(
    scene_data: xr.Dataset,
    pixel_scale: u.Quantity,
    rows: int,
    cols: int,
) -> xr.DataArray:
    """
    Project objects onto detector. Converting scene from arcsec to detector coordinates.

    Parameters
    ----------
    scene_data : xr.Dataset
        Scene dataset with wavelength and flux information to project onto detector.
    pixel_scale : u.Quantity
        Pixel sclae of instrument. Unit: arcsec/pixel.
    rows : int
        Rows of detector.
    cols : int
        Columns of detector.

    Returns
    -------
    photon_3d : xr.DataArray
        Projected objects in detector coordinates.

    """
    # we project the stars in the FOV:
    stars_coords = SkyCoord(
        scene_data["x"].values * u.arcsec,
        scene_data["y"].values * u.arcsec,
        frame="icrs",
    )

    # coordinates of telescope pointing
    telescope_ra: u.Quantity = (scene_data["x"].values * u.arcsec).mean()
    telescope_dec: u.Quantity = (scene_data["y"].values * u.arcsec).mean()
    coords_detector = SkyCoord(ra=telescope_ra, dec=telescope_dec, unit="degree")

    # using World Coordinate System (WCS) to convert to pixel
    # more info: https://heasarc.gsfc.nasa.gov/docs/fcg/standard_dict.html
    w = wcs.WCS(naxis=2)

    # define cdelt: coordinate increment along axis
    cdelt = (np.array([-1.0, 1.0]) * pixel_scale).to(u.deg / u.pixel)
    w.wcs.cdelt = cdelt

    # define crpix: coordinate system reference pixel
    crpix = np.array([rows / 2, cols / 2]) * u.pixel
    w.wcs.crpix = crpix

    # define crval: coordinate system value at reference pixel
    w.wcs.crval = [coords_detector.ra.deg, coords_detector.dec.deg]

    # define crota: coordinate system rotation angle
    w.wcs.crota = [0, -0]

    # define ctype: name of the coordinate axis
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    """
    # Other possible method to convert to pixel usingscopesim:
    # https://github.com/AstarVienna/ScopeSim/blob/dev_master/scopesim/optics/image_plane_utils.py#L698
    # gives different result.
    # da = cdelt[0]
    # db = cdelt[1]
    # x0 = crpix[0]
    # y0 = crpix[1]
    # a0 = selected_data["x"].values * u.arcsec
    # b0 = selected_data["y"].values * u.arcsec
    # a = float(telescope_ra) * u.deg
    # b = float(telescope_dec) * u.deg
    # convert stars coordinate to detector coordinates
    # detector_coords_x = x0 + 1. / da * (a - a0)
    # detector_coords_y = y0 + 1. / db * (b - b0)
    """

    detector_coords_x = np.round(
        w.world_to_pixel_values(stars_coords.ra, stars_coords.dec)[0]
    )
    detector_coords_y = np.round(
        w.world_to_pixel_values(stars_coords.ra, stars_coords.dec)[1]
    )
    scene_data["detector_coords_x"] = xr.DataArray(
        detector_coords_x, dims="ref", attrs={"units": "pixel"}
    )
    scene_data["detector_coords_y"] = xr.DataArray(
        detector_coords_y, dims="ref", attrs={"units": "pixel"}
    )

    # make sure that only stars inside the detector
    selected_data_new = scene_data.copy(deep=True)
    selected_data_query = (
        selected_data_new.query(ref="detector_coords_x > 0")
        .query(ref=f"detector_coords_x < {cols}")
        .query(ref=f"detector_coords_y < {rows}")
        .query(ref="detector_coords_y > 0")
    )

    # convert to int
    selected_data2 = selected_data_query.copy(deep=True)
    selected_data2["detector_coords_x"] = selected_data2["detector_coords_x"].astype(
        int
    )
    selected_data2["detector_coords_y"] = selected_data2["detector_coords_y"].astype(
        int
    )

    # get empty array in shape of the 3D datacube of the detector
    projection = np.zeros([selected_data2.wavelength.size, rows, cols])

    # fill in projection of objects in detector coordinates
    for x, group_x in selected_data2.groupby("detector_coords_x"):
        for y, group_y in group_x.groupby("detector_coords_y"):
            projection[:, int(y), int(x)] += np.array(
                group_y["converted_flux"].squeeze()
            )

    photon_3d = xr.DataArray(
        projection,
        dims=["wavelength", "y", "x"],
        coords={"wavelength": selected_data2.wavelength},
        attrs={"units": selected_data2.converted_flux.units},
    )

    return photon_3d


def aperture_3d(
    detector: Detector,
    pixel_scale: float,
    aperture: float,
):
    """Convert scene in ph/(cm2 nm s) to 3D photon in ph/nm s.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    pixel_scale : float
        Pixel scale. Unit: arcsec/pixel.
    aperture : float
        Collecting area of the telescope. Unit: m.
    """
    # get scene data from detector
    scene_data = detector.scene.data["/list/0"].to_dataset()
    # get flux in ph/(s nm cm^2)
    flux = u.Quantity(np.asarray(scene_data["flux"]), unit=scene_data["flux"].units)
    # get time in s
    time = detector.time_step * u.s
    # get aperture in m
    aperture = aperture * u.m

    # get flux converted to ph/nm
    converted_flux: u.Quantity = convert_flux(
        flux=flux, t_exp=time, aperture=aperture
    )  # .to(u.ph / u.nm)

    # load converted flux to scene_data dataset
    scene_data["converted_flux"] = xr.DataArray(
        converted_flux,
        dims=["ref", "wavelength"],
        attrs={"units": str(converted_flux.unit)},
    )

    projection = project_objects_to_detector(
        scene_data=scene_data,
        pixel_scale=pixel_scale * u.arcsec / u.pixel,
        rows=detector.geometry.row,
        cols=detector.geometry.col,
    )

    detector.photon3d = Photon3D(projection)
