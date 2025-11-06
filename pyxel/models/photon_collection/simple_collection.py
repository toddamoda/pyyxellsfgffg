#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Convert scene to photon with simple collection model."""

import astropy.units as u
import numpy as np
import xarray as xr
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.units import Quantity

from pyxel.data_structure import Scene, SceneCoordinates
from pyxel.detectors import Detector, WavelengthHandling


def extract_wavelength(
    scene: Scene,
    wavelengths: xr.DataArray,
) -> xr.Dataset:
    """Extract xarray Dataset of Scene for selected wavelength band."""
    # retrieve scene data, convert it to xarray and interpolate it
    interpolated_wavelengths = scene.to_xarray().interp(wavelength=wavelengths)
    return interpolated_wavelengths


def integrate_flux(
    flux: xr.DataArray,
) -> xr.DataArray:
    """Integrate flux in photon/(s nm cm2) along wavelength -> photon/(s cm2)."""
    integrated_flux = flux.integrate(coord="wavelength")
    integrated_flux.attrs["units"] = str(u.Unit(flux.units) * u.nm)
    return integrated_flux


# ---- NEW: helper to integrate a RATE over readout windows (time) ----------------
def integrate_rate_over_windows(
    rate: xr.DataArray,  # units: ph / (s cm2)
    readout_times: np.ndarray,  # seconds, monotonic increasing
) -> xr.DataArray:
    """
    Integrate photon rate ph/(s cm2) over time windows -> ph/cm2 per window.

    Returns DataArray with dims ('readout_time', *rate.dims_without_time)
    """
    if "time" not in rate.dims:
        raise ValueError("Expected a 'time' dimension for temporal integration.")

    counts_per_window = []
    for i in range(len(readout_times) - 1):
        t0, t1 = readout_times[i], readout_times[i + 1]
        # integrate along time to get ph/cm2 in this interval
        window_counts = rate.sel(time=slice(t0, t1)).integrate(coord="time")
        counts_per_window.append(window_counts.expand_dims(readout_time=[i]))

    out = xr.concat(counts_per_window, dim="readout_time")
    # units: rate.units * s
    out.attrs["units"] = str(u.Unit(rate.attrs.get("units", "1 / (cm2 s)")) * u.s)
    return out


# ---- NEW: area conversion for counts already integrated in time ----------------
def convert_counts_area(
    counts_per_cm2: Quantity,  # ph/cm2
    aperture: Quantity,  # m
) -> Quantity:
    """Convert ph/cm2 to photons by multiplying with collecting area."""
    col_area = (
        np.pi * (aperture * 1e2 / 2) ** 2
    )  # m -> cm (1e2), area of circular aperture
    return counts_per_cm2 * col_area


def convert_flux(
    flux: Quantity,
    t_exp: Quantity,
    aperture: Quantity,
) -> Quantity:
    """Convert rate (ph/(s cm2)) to photons (or per-nm), multiplying by exposure and area."""
    # TODO: check aperture factor 1e2 correct?!
    # TODO: add unit test.
    col_area = np.pi * (aperture * 1e2 / 2) ** 2
    flux_converted = flux * t_exp * col_area
    return flux_converted


def project_objects_to_detector(
    scene_data: xr.Dataset,
    pixel_scale: Quantity,
    rows: int,
    cols: int,
) -> xr.Dataset:
    """
    Project objects onto detector. Converting scene from arcsec to detector coordinates.
    """
    # we project the stars in the FOV:
    stars_coords = SkyCoord(
        Quantity(scene_data["x"].values, unit="arcsec"),
        Quantity(scene_data["y"].values, unit="arcsec"),
        frame="icrs",
    )

    # coordinates of telescope pointing
    scene_coord: SceneCoordinates = SceneCoordinates.from_dataset(scene_data)
    telescope_ra: Quantity = scene_coord.right_ascension
    telescope_dec: Quantity = scene_coord.declination
    coords_detector = SkyCoord(ra=telescope_ra, dec=telescope_dec, unit="degree")

    # using World Coordinate System (WCS) to convert to pixel
    w = wcs.WCS(naxis=2)

    cdelt = (np.array([-1.0, 1.0]) * pixel_scale).to("deg / pix")
    w.wcs.cdelt = cdelt

    crpix = Quantity(np.array([rows / 2, cols / 2]), unit="pix")
    w.wcs.crpix = crpix

    w.wcs.crval = [coords_detector.ra.deg, coords_detector.dec.deg]
    w.wcs.crota = [0, -0]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

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

    selected_data_query = (
        scene_data.copy(deep=True)
        .query(ref="detector_coords_x > 0")
        .query(ref=f"detector_coords_x < {cols}")
        .query(ref=f"detector_coords_y < {rows}")
        .query(ref="detector_coords_y > 0")
    )

    if selected_data_query.sizes["ref"] == 0:
        raise ValueError(
            "No objects projected in the detector. "
            "To resolve this issue you can use function 'pyxel.display_scene'"
        )

    selected_data_query["detector_coords_x"] = selected_data_query[
        "detector_coords_x"
    ].astype(int)
    selected_data_query["detector_coords_y"] = selected_data_query[
        "detector_coords_y"
    ].astype(int)

    return selected_data_query


def aggregate_monochromatic(data: xr.Dataset, rows: int, cols: int) -> np.ndarray:
    """Aggregate a 3D data array containing fluxes into a 2D array."""
    projection_2d: np.ndarray = np.zeros([rows, cols])
    for x, group_x in data.groupby("detector_coords_x"):
        for y, group_y in group_x.groupby("detector_coords_y"):
            projection_2d[int(y), int(x)] += group_y["converted_flux"].values.sum()
    return projection_2d


def aggregate_multiwavelength(data: xr.Dataset, rows: int, cols: int) -> xr.DataArray:
    """Aggregate a 3D ``DataArray`` containing fluxes into a 3D ``DataArray``."""
    projection = np.zeros([data.wavelength.size, rows, cols])
    for x, group_x in data.groupby("detector_coords_x"):
        for y, group_y in group_x.groupby("detector_coords_y"):
            projection[:, int(y), int(x)] += np.array(
                group_y["converted_flux"].sum(dim="ref")
            )

    projection_3d: xr.DataArray = xr.DataArray(
        projection,
        dims=["wavelength", "y", "x"],
        coords={"wavelength": data.wavelength},
        attrs={"units": data.converted_flux.units},
    )
    return projection_3d


# ---- NEW: aggregate time windows to (readout_time, y, x) -----------------------
def aggregate_time(data: xr.Dataset, rows: int, cols: int) -> xr.DataArray:
    """Aggregate per-ref counts into a (readout_time, y, x) cube."""
    n_t = data.readout_time.size
    projection = np.zeros([n_t, rows, cols])

    for x, group_x in data.groupby("detector_coords_x"):
        for y, group_y in group_x.groupby("detector_coords_y"):
            # sum over ref for each readout_time
            summed = np.array(group_y["converted_flux"].sum(dim="ref"))
            projection[:, int(y), int(x)] += summed

    projection_3d: xr.DataArray = xr.DataArray(
        projection,
        dims=["readout_time", "y", "x"],
        coords={"readout_time": data.readout_time},
        attrs={"units": data.converted_flux.units},
    )
    return projection_3d


# TODO: Add unit tests
def _extract_wavelength(
    resolution: int | None,
    filter_band: tuple[float, float] | None,
    default_wavelength_handling: float | WavelengthHandling | None,
) -> xr.DataArray:
    """Extract wavelength."""
    if filter_band is not None:
        first_band, last_band = filter_band
        if not (0 < first_band < last_band):
            raise ValueError(
                f"'filter_band' must be increasing and strictly positive. Got: {filter_band!r}"
            )

        if resolution is not None:
            if resolution <= 0.0:
                raise ValueError(f"Expected 'resolution' > 0. Got: {resolution!r}")
            step_size = resolution
        else:
            if not isinstance(default_wavelength_handling, WavelengthHandling):
                raise ValueError(
                    "No 'resolution' provided for model 'simple_collection'. Please provide 'resolution'` "
                    "parameters in the detector environment wavelength or as input into this model directly."
                )
            step_size = default_wavelength_handling.resolution

    else:
        if resolution is not None:
            if resolution <= 0.0:
                raise ValueError(f"Expected 'resolution' > 0. Got: {resolution!r}")

            if not isinstance(default_wavelength_handling, WavelengthHandling):
                raise ValueError(
                    "No 'filter_band' provided for model 'simple_collection'. Please provide 'resolution'` "
                    "parameters in the detector environment wavelength or as input into this model directly."
                )

            first_band = default_wavelength_handling.cut_on
            last_band = default_wavelength_handling.cut_off
            step_size = resolution
        else:
            if not isinstance(default_wavelength_handling, WavelengthHandling):
                raise ValueError(
                    "'filter_band' and 'resolution' have both to be provided either as model arguments or in the "
                    "detector environment. Please provide them in the detector in the detector wavelength or "
                    "as input into this model directly"
                )

            first_band = default_wavelength_handling.cut_on
            last_band = default_wavelength_handling.cut_off
            step_size = default_wavelength_handling.resolution

    wavelengths: xr.DataArray = WavelengthHandling(
        cut_on=first_band,
        cut_off=last_band,
        resolution=step_size,
    ).get_wavelengths()

    return wavelengths


def simple_collection(
    detector: Detector,
    aperture: float,
    filter_band: tuple[float, float] | None = None,
    resolution: int | None = None,
    pixel_scale: float | None = None,
    integrate_wavelength: bool = True,
    # ---- NEW OPTIONALS (backward-compatible) ----
    integrate_time: bool = False,
):
    """Convert scene in ph/(cm2 nm s) to photon in ph/nm s or ph s.

    If the Scene contains a 'time' coordinate and 'integrate_time=True',
    the model integrates the (wavelength-integrated) photon rate over
    the provided readout windows to produce a (readout_time, y, x) cube.
    """
    if aperture <= 0.0:
        raise ValueError(f"Expected 'aperture' > 0. Got: {aperture!r}")

    if detector.scene == Scene():
        raise ValueError(
            "Missing 'scene' in 'detector'. "
            "To resolve this issue, you must use a model that generate a 'Scene' "
            "from the 'Photon Collection' group.\nConsider using the 'load_star_map' "
            "model."
        )

    if detector.photon.ndim != 0:
        raise ValueError(
            "Photons are already defined in 'detector.photon'. "
            "To resolve this issue, you must have no photons before running this model."
        )

    if pixel_scale is None:
        if detector.geometry._pixel_scale is None:
            raise ValueError(
                "Pixel scale is not defined. It must be either provided in the detector geometry "
                "or as model argument."
            )
        pixel_scale_arcsec: Quantity = Quantity(
            detector.geometry.pixel_scale, unit="arcsec/pixel"
        )
    else:
        if pixel_scale <= 0.0:
            raise ValueError(f"Expected 'pixel_scale' > 0. Got: {pixel_scale!r}")
        pixel_scale_arcsec = Quantity(pixel_scale, unit="arcsec/pixel")

    wavelengths: xr.DataArray = _extract_wavelength(
        resolution=resolution,
        filter_band=filter_band,
        default_wavelength_handling=detector.environment._wavelength,
    )

    # get dataset for given wavelength and scene object.
    scene_data: xr.Dataset = extract_wavelength(
        scene=detector.scene,
        wavelengths=wavelengths,
    )

    # get time in s
    time = Quantity(detector.time_step, unit="s")
    # get aperture in m
    aperture_q = Quantity(aperture, unit="m")

    # ---- Branch A: wavelength-integrated path (default) ----------------------
    if integrate_wavelength:
        # integrate along wavelength -> rate ph/(s cm2)
        integrated_rate: xr.DataArray = integrate_flux(flux=scene_data["flux"])
        rate = Quantity(integrated_rate, unit=integrated_rate.units)

        # ---- If time integration is requested and time coord exists ----------
        if integrate_time and "time" in scene_data.dims:
            # Require readout times on detector (set by Observation)
            if not hasattr(detector, "readout_times"):
                raise ValueError(
                    "Time integration requested but 'detector.readout_times' is missing."
                )

            # integrate rate over readout windows -> counts per cm2
            counts_per_cm2: xr.DataArray = integrate_rate_over_windows(
                rate=integrated_rate, readout_times=np.asarray(detector.readout_times)
            )
            counts_q = Quantity(
                counts_per_cm2, unit=counts_per_cm2.attrs["units"]
            )  # ph/cm2

            # convert to photons using aperture area
            converted_counts = convert_counts_area(
                counts_per_cm2=counts_q, aperture=aperture_q
            )

            # attach to scene_data with dims ('ref','readout_time')
            scene_data["converted_flux"] = xr.DataArray(
                converted_counts,
                dims=["ref", "readout_time"],
                attrs={"units": str(converted_counts.unit)},
            )

            # project and aggregate to (readout_time, y, x)
            photon_projected = project_objects_to_detector(
                scene_data=scene_data,
                pixel_scale=pixel_scale_arcsec,
                rows=detector.geometry.row,
                cols=detector.geometry.col,
            )

            photon_projection_time: xr.DataArray = aggregate_time(
                data=photon_projected,
                rows=detector.geometry.row,
                cols=detector.geometry.col,
            )

            detector.photon.array_3d = (
                photon_projection_time  # dims: (readout_time, y, x)
            )

        else:
            # Original 2D behaviour: multiply rate by exposure time and area
            converted_flux_2d: Quantity = convert_flux(
                flux=rate, t_exp=time, aperture=aperture_q
            )

            scene_data["converted_flux"] = xr.DataArray(
                converted_flux_2d,
                dims="ref",
                attrs={"units": str(converted_flux_2d.unit)},
            )

            photon_projected = project_objects_to_detector(
                scene_data=scene_data,
                pixel_scale=pixel_scale_arcsec,
                rows=detector.geometry.row,
                cols=detector.geometry.col,
            )

            photon_projection_2d: np.ndarray = aggregate_monochromatic(
                data=photon_projected,
                rows=detector.geometry.row,
                cols=detector.geometry.col,
            )

            detector.photon.array_2d = photon_projection_2d

    # ---- Branch B: multiwavelength (kept as-is; no time aggregation here) ----
    else:
        flux_with_weight: xr.DataArray = scene_data["flux"] * scene_data["weight"]
        flux = Quantity(flux_with_weight, unit=scene_data["flux"].units)

        converted_flux_3d: Quantity = convert_flux(
            flux=flux,
            t_exp=time,
            aperture=aperture_q,
        )

        scene_data["converted_flux"] = xr.DataArray(
            converted_flux_3d,
            dims=["ref", "wavelength"],
            attrs={"units": str(converted_flux_3d.unit)},
        )

        photon_projected = project_objects_to_detector(
            scene_data=scene_data,
            pixel_scale=pixel_scale_arcsec,
            rows=detector.geometry.row,
            cols=detector.geometry.col,
        )

        photon_projection_3d: xr.DataArray = aggregate_multiwavelength(
            data=photon_projected,
            rows=detector.geometry.row,
            cols=detector.geometry.col,
        )

        detector.photon.array_3d = photon_projection_3d
