#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Wrapper to create simple graphs using the source extractor package"""

import numpy as np
import sep
import matplotlib.pyplot as plt
from pyxel.detectors import Detector


def imshow_detector(
        detector: Detector
) -> None:
    """Takes in the detector object and shows the array values as an image to the user.

    Parameters
    -----------
    detector : Detector
        Pyxel Detector object.
    """
    data = detector['pixel'][0].values
    m, s = np.mean(data), np.std(data)
    plt.imshow(data, interpolation='nearest', cmap='gray', vmin=m - s, vmax=m + s, origin='lower')
    plt.colorbar();


def get_background(
        detector: Detector,
):
    """Gets the background of an image using the SEP library.

    Parameters
    -----------
    detector : Detector
        Pyxel Detector object."""

    data = detector['pixel'][0].values

    return sep.Background(data, bw=64, bh=64, fw=3, fh=3)


def get_background_image(
        detector: Detector,
):
    bkg = get_background(detector)
    return bkg.back()


def get_background_rms(
        detector: Detector,
):
    bkg = get_background(detector)
    return bkg.rms()


def subtract_background(
        detector: Detector,
):
    data = detector['pixel'][0].values
    bkg = get_background(detector)
    return data - bkg


def extract_roi(
        detector: Detector,
        thresh
):
    data = detector['pixel'][0].values
    return sep.extract(data, thresh=thresh, segmentation_map=True)
