#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Convert scene to photon with aperture model."""

import astropy.units as u
import numpy as np
import xarray as xr
from astropy import wcs
from astropy.coordinates import SkyCoord

from pyxel.data_structure import Scene
from pyxel.detectors import Detector


def extract_wavelength(
    scene: Scene,
    wavelength_band: tuple[float, float],
) -> xr.Dataset:
    """Extract xarray Dataset of Scene for selected wavelength band.

    Parameters
    ----------
    scene : Scene
        Pyxel scene object.
    wavelength_band : float
        Selected wavelength band. Unit: nm.

    Returns
    -------
    selected_data : xr.Dataset

    Examples
    --------
    >>> scene = Scene(...)
    >>> extract_wavelength(scene=scene, wavelength_band=[500, 900])
    <xarray.Dataset>
    Dimensions:     (ref: 345, wavelength: 201)
    Coordinates:
      * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
      * wavelength  (wavelength) float64 500.0 502.0 504.0 ... 896.0 898.0 900.0
    Data variables:
        x           (ref) float64 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
        y           (ref) float64 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
        weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
        flux        (ref, wavelength) float64 0.2331 0.231 0.2269 ... 2.213 2.212
    """

    start_wavelength, end_wavelength = wavelength_band

    if start_wavelength > end_wavelength:
        raise ValueError(
            "First input in wavelength_band needs to be smaller than the second."
        )

    data = scene.to_xarray()
    # get dataset with x, y, weight and flux of scene for selected wavelength band.
    selected_data: xr.Dataset = data.sel(
        wavelength=slice(start_wavelength, end_wavelength)
    )

    return selected_data


def integrate_flux(
    flux: xr.DataArray,
) -> xr.DataArray:
    """Integrate flux in photon/(s nm cm2) along the wavelength band in nm and return integrated flux in photon/(s cm2).

    Parameters
    ----------
    flux : xr.DataArray
        Flux. Unit: photon/(s nm cm2).

    Returns
    -------
    integrated_flux : xr.DataArray
        Flux integrated alaong wavelangth band. Unit: photon/(s cm2).

    Examples
    --------
    >>> flux
    <xarray.DataArray 'flux' (ref: 345, wavelength: 201)>
    array([[0.23309256, 0.23099403, 0.22690838, ..., 0.74632666, 0.74254087,
            0.74107508],
           [0.02540123, 0.02539306, 0.02532492, ..., 0.02315146, 0.02275346,
            0.02240911],
           [0.00848251, 0.00849082, 0.00835927, ..., 0.01687145, 0.01677347,
            0.01674323],
           ...,
           [0.0086873 , 0.00874152, 0.0088429 , ..., 0.01047889, 0.01037253,
            0.01032473],
           [0.28250153, 0.27994777, 0.27599212, ..., 0.30550521, 0.30414266,
            0.30421148],
           [3.82353376, 3.86376387, 3.88179622, ..., 2.22050587, 2.21307412,
            2.21216093]])
    Coordinates:
      * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
      * wavelength  (wavelength) float64 500.0 502.0 504.0 ... 896.0 898.0 900.0
    Attributes:
        units:    ph / (cm2 nm s)
    >>> integrate_flux(flux=flux)
    <xarray.DataArray 'flux' (ref: 345)>
    array([2.13684421e+02, 1.01716326e+01, 5.69110647e+00, 1.17371054e+01,
           2.55767948e+01, 6.91026764e+00, 3.79706245e+00, 1.04048130e+01,
           ...
           6.00547211e+00, 6.19314865e+00, 9.97548328e+00, 5.88036380e+00,
           1.10089431e+01, 1.40244956e+01, 4.23104795e+00, 1.28482189e+02,
           1.18302668e+03])
    Coordinates:
      * ref      (ref) int64 0 1 2 3 4 5 6 7 8 ... 337 338 339 340 341 342 343 344
    Attributes:
        units:    ph / (cm2 s)
    """
    # integrate flux along coordinate wavelength
    integrated_flux = flux.integrate(coord="wavelength")
    integrated_flux.attrs["units"] = str(u.Unit(flux.units) * u.nm)

    return integrated_flux


def convert_flux(
    flux: u.Quantity,
    t_exp: float,
    aperture: float,
) -> u.Quantity:
    """Convert flux in photon/(s cm2) to photon/(s pixel).

    Parameters
    ----------
    flux : u.Quantity
        Flux. Unit: photon/pixel/s/cm2.
    t_exp : float
        Exposure time. Unit: s.
    aperture : float
        Collecting area of the telescope. Unit: m.

    Returns
    -------
    u.Quantity
        Converted flux in photon/s/pixel.

    Examples
    --------
    >>> flux
     <Quantity [2.13684421e+02, 1.01716326e+01, 5.69110647e+00, 1.17371054e+01,
           2.55767948e+01, 6.91026764e+00, 3.79706245e+00, 1.04048130e+01,
           2.67257165e+02, 1.50122471e+01, 5.76777354e+00, 4.18198718e+00,
           ...
           1.18302668e+03] ph / (cm2 s)>
    >>> convert_flux(flux=flux, t_exp=6000 * u.s, aperture=0.1267)
    <Quantity [1.61646841e+08, 7.69458192e+06, 4.30517760e+06, 8.87882234e+06,
           1.93481961e+07, 5.22744209e+06, 2.87238137e+06, 7.87097696e+06,
           ...
           2.10520464e+07, 9.04914055e+06, 4.45057621e+07, 3.61838622e+07,
           4.44387021e+09, 4.28110535e+06, 6.37296766e+06, 9.86548629e+06,
            8.94929654e+08] ph / cm2>
    """

    col_area = np.pi * (aperture * 1e2 / 2) ** 2
    flux_converted = flux * t_exp * col_area

    return flux_converted


def project_objects_to_detector(
    selected_data: xr.Dataset,
    pixel_scale: u.Quantity,
    rows: int,
    cols: int,
) -> np.ndarray:
    """
    Project objects onto detector. Converting scene from arcsec to detector coordinates.

    Parameters
    ----------
    selected_data : xr.Dataset
        Dataset with selected wavelength band and flux to project onto detector.
    pixel_scale : u.Quantity
        Pixel sclae of instrument. Unit: arcsec/pixel.
    rows : int
        Rows of detector.
    cols : int
        Columns of detector.

    Returns
    -------
    projection : np.ndarray
        Projected objects in detector coordinates.

    Examples
    --------
    >>> selected_data
    <xarray.Dataset>
    Dimensions:            (ref: 345, wavelength: 201)
    Coordinates:
      * ref                (ref) int64 0 1 2 3 4 5 6 ... 338 339 340 341 342 343 344
      * wavelength         (wavelength) float64 500.0 502.0 504.0 ... 898.0 900.0
    Data variables:
        x                  (ref) float64 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
        y                  (ref) float64 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
        weight             (ref) float64 11.49 14.13 15.22 ... 15.21 11.51 8.727
        flux               (ref, wavelength) float64 0.2331 0.231 ... 2.213 2.212
        converted_flux     (ref) float64 1.616e+08 7.695e+06 ... 9.719e+07 8.949e+08
        detector_coords_x  (ref) float64 1.307e+03 1.252e+03 ... 2.748e+03 2.809e+03
        detector_coords_y  (ref) float64 1.454e+03 1.487e+03 ... 2.79e+03 2.859e+03
    >>> project_objects_to_detector(
    ...     selected_data=selected_data,
    ...     pixel_scale=1.65 * u.arcsec / u.pixel,
    ...     rows=4096,
    ...     cols=4132,
    ... )
    array([[0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           ...,
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.]])
    """
    # we project the stars in the FOV:
    stars_coords = SkyCoord(
        selected_data["x"].values * u.arcsec,
        selected_data["y"].values * u.arcsec,
        frame="icrs",
    )

    # coordinates of telescope pointing
    telescope_ra: u.Quantity = (selected_data["x"].values * u.arcsec).mean()
    telescope_dec: u.Quantity = (selected_data["y"].values * u.arcsec).mean()
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
    selected_data["detector_coords_x"] = xr.DataArray(
        detector_coords_x, dims="ref", attrs={"units": "pixel"}
    )
    selected_data["detector_coords_y"] = xr.DataArray(
        detector_coords_y, dims="ref", attrs={"units": "pixel"}
    )

    # make sure that only stars inside the detector
    selected_data_new = selected_data.copy(deep=True)
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

    # get empty array in shape of the detector
    projection = np.zeros([rows, cols])

    # fill in projection of objects in detector coordinates
    for x, group_x in selected_data2.groupby("detector_coords_x"):
        for y, group_y in group_x.groupby("detector_coords_y"):
            projection[int(y), int(x)] = group_y["converted_flux"].values.sum()

    return projection


def simple_aperture(
    detector: Detector,
    pixel_scale: float,
    aperture: float,
    wavelength_band: tuple[float, float],
):
    """Convert scene(photon/s/cm2) to photon.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    pixel_scale : float
        Pixel scale. Unit: arcsec/pixel.
    aperture : float
        Collecting area of the telescope. Unit: m.
    wavelength_band : tuple[float, float]
        Wavelength band. Unit: nm.
    """
    # get dataset for given wavelength and scene object.
    selected_data: xr.Dataset = extract_wavelength(
        scene=detector.scene, wavelength_band=wavelength_band
    )

    # integrate flux
    integrated_flux: xr.DataArray = integrate_flux(flux=selected_data["flux"])

    # get flux in ph/s/cm^2
    flux = u.Quantity(integrated_flux, unit=integrated_flux.units)
    # get time in s
    time = detector.time_step * u.s

    # get flux converted to ph
    converted_flux: u.Quantity = convert_flux(flux=flux, t_exp=time, aperture=aperture)

    # load converted flux to selected dataset
    selected_data["converted_flux"] = xr.DataArray(
        converted_flux, dims="ref", attrs={"units": str(converted_flux.unit)}
    )

    projection = project_objects_to_detector(
        selected_data=selected_data,
        pixel_scale=pixel_scale * u.arcsec / u.pixel,
        rows=detector.geometry.row,
        cols=detector.geometry.col,
    )

    detector.photon.array = projection
