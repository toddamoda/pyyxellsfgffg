#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Wrapper to create simple graphs using the source extractor package."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sep
import xarray as xr
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
    thresh: int = 50,
    minarea: int = 5,
) -> None:
    """Extract the roi data converts it to xarray dataset and saves the information to the final result.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    thresh : int
        threshold above which information from the image array is extracted
    minarea : int
        minimum area of elements required that are above the threshold for the extractor to extract information
    """
    data_2d = detector.pixel.array
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

    detector.processed_data.append(ds)
