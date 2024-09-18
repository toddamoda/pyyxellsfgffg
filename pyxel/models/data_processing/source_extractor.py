#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Wrapper to create simple graphs using the source extractor package."""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

# Import 'DataTree'
try:
    from xarray.core.datatree import DataTree
except ImportError:
    from datatree import DataTree  # type: ignore[assignment]

from matplotlib.patches import Ellipse

from pyxel.detectors import Detector


def show_detector(image_2d: np.ndarray, vmin=0, vmax=100) -> None:
    """Take in the detector object and shows the array values as an image to the user.

    Parameters
    ----------
    image_2d
        2D image array .
    """
    im = plt.imshow(
        image_2d,
        interpolation="nearest",
        cmap="gray",
        vmin=vmin,
        vmax=vmax,
        origin="lower",
    )
    plt.colorbar(im)


def get_background(image_2d: np.ndarray):
    """Get the background of an image using the SEP library.

    Parameters
    ----------
    image_2d
        2d image array.
    """
    try:
        import sep
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'sep'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install sep'"
        ) from exc

    return sep.Background(image_2d)


def get_background_image(image_2d: np.ndarray):
    """Get the background of an image and converts it to a 2D-array of the same shape of the original input image.

    Parameters
    ----------
    image_2d
        2D image array .
    """
    bkg = get_background(image_2d)
    return bkg.back()


def get_background_data(image_2d: np.ndarray):
    """Get the background rms array [0], the global average rms [1] and the global average background value [2].

    Parameters
    ----------
    image_2d
        2D image array .
    """
    bkg = get_background(image_2d)
    return bkg.rms(), bkg.globalrms, bkg.globalback


def subtract_background(image_2d: np.ndarray):
    """Return a background subtracted numpy array.

    Parameters
    ----------
    image_2d
        2D image array .
    """
    bkg = get_background(image_2d)
    return image_2d - bkg


def extract_roi(
    image_2d: np.ndarray, thresh: int, minarea: int = 5, name: str = "pixel"
):
    """Return a structured numpy array that gives information on the roi found based on the threshold and minea given.

    Parameters
    ----------
    image_2d : np.ndarray
        2D image array
    thresh : int
        signal level above which signifies a region of interest
    minarea : int
        minimum area of elements required that are above the threshold for the extractor to extract information
    """
    try:
        import sep
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'sep'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install sep'"
        ) from exc

    return sep.extract(image_2d, thresh=thresh, segmentation_map=True, minarea=minarea)


def plot_roi(data: np.ndarray, roi) -> None:
    """Plot the input data on a graph and overlays ellipses over the roi's found by the extract function.

    Parameters
    ----------
    data : np.ndarray
        2D image array
    roi : np.ndarray / xarray.Dataset
        structured numpy array or xarray dataset of extracted data
    """
    fig, ax = plt.subplots()
    m, s = np.mean(data), np.std(data)
    im = ax.imshow(
        data,
        interpolation="nearest",
        cmap="gray",
        vmin=m - s,
        vmax=m + s,
        origin="lower",
    )

    # plot an ellipse for each object
    for i in range(len(roi["x"])):
        e = Ellipse(
            xy=(roi["x"][i], roi["y"][i]),
            width=6 * roi["a"][i],
            height=6 * roi["b"][i],
            angle=roi["theta"][i] * 180.0 / np.pi,
        )
        e.set_facecolor("none")
        e.set_edgecolor("red")
        ax.add_artist(e)
    plt.colorbar(im)


def extract_roi_to_xarray(
    detector: Detector,
    array_type: str = "pixel",
    thresh: int = 50,
    minarea: int = 5,
) -> None:
    """Extract the roi data converts it to xarray dataset and saves the information to the final result.

    A warning is generated if the processed data_array is empty.

    Parameters
    ----------
    array_type
    detector : Detector
        Pyxel Detector object.
    thresh : int
        Threshold pixel value above which information from the image array is extracted
    minarea : int
        Minimum area of pixels required that are above the threshold for the extractor to extract information

    Raises
    ------
    ValueError
        If parameter 'array_type' is not 'pixel','signal','image',photon' or 'charge'

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/data_processing/source_extractor/SEP_exposure`.
    """
    try:
        import sep
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'sep'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install sep'"
        ) from exc

    if array_type == "pixel":
        data_2d: np.ndarray = detector.pixel.array
    elif array_type == "signal":
        data_2d = detector.signal.array
    elif array_type == "image":
        data_2d = detector.image.array
    elif array_type == "photon":
        data_2d = detector.photon.array
    elif array_type == "charge":
        data_2d = detector.charge.array
    else:
        raise ValueError(
            "Incorrect array_type. Must be one of 'pixel','signal','image',photon' or"
            " 'charge'."
        )

    data_2d = np.asarray(data_2d, dtype=float)
    if np.all(data_2d == 0):
        warnings.warn(f"{array_type} data array is empty", stacklevel=2)

    objects, segmap = sep.extract(
        data_2d, thresh=thresh, minarea=minarea, segmentation_map=True
    )

    ds_objects: xr.Dataset = pd.DataFrame(objects).to_xarray()

    num_y, num_x = segmap.shape

    ds_segmap = xr.Dataset()
    ds_segmap["segmap"] = xr.DataArray(
        segmap,
        dims=["image_y", "image_x"],
        coords={"image_y": range(num_y), "image_x": range(num_x)},
    )

    ds = ds_objects.assign_coords(image_y=range(num_y), image_x=range(num_x)).merge(
        ds_segmap
    )

    detector.data["/source_extractor"] = DataTree(ds)
