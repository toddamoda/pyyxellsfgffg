#  Copyright (c) University College London, 2025.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""
shield module for the PyXel simulation.

This module is used in photon_collection

-------------------------------------------------------------------------------

+--------------+----------------------------------+---------------------------+
| Author       | Name                             | Creation                  |
+--------------+----------------------------------+---------------------------+
| Zach Clare   | shield                           | Thu Jul  3 16:21:15 2025  |
+--------------+----------------------------------+---------------------------+

+-----------------+-------------------------------------+---------------------+
| Contributor     | Name                                | Creation            |
+-----------------+-------------------------------------+---------------------+
| Zach Clare      | shield.py                           | 07/03/2025          |
+-----------------+-------------------------------------+---------------------+

This module will draw a light shield in a specified place of the photon array
allowing zero photons to pass through. All later stages of processing will
still happen. This allows the simuation of dark regions to contextualise
science results.

Note that widths and box sizes are inclusive. For example, if you want a 3x3
box shield starting on pixel (60,50), pass shield_start=(60,50) and
shield_end=(62,52).

Model reference in the YAML config file
=======================================

.. code-block:: yaml

    pipeline:

      # Add shield border around image on all sides 8px deep
      - name: shield_border
        func: pyxel.models.photon_collection.shield_border
        enabled: true
        arguments:
          width: 8

      # Add shield box in specific rectangle of image
      - name: shield_box
        func: pyxel.models.photon_collection.shield_box
        enabled: false
        arguments:
          shield_start: [20, 20]
          shield_end: [30, 50]

Useful links
============

ReadTheDocs documentation
https://sphinx-rtd-theme.readthedocs.io/en/latest/index.html

"""

from pyxel.detectors import Detector

import numpy as np


def get_mask_shape_box(
        shape: tuple[int, int],
        shield_start: tuple[int, int],
        shield_end: tuple[int, int]
    ) -> np.array:
    """Defines a binary matrix representing where the light shield is not
    present somewhere within the array.
    
    0 represents light shield over that pixel.
    1 represents no light shield over that pixel.
    
    Parameters
    ----------
    shape: tuple[int, int]
    shield_start: tuple[int, int]
    shield_end: tuple[int, int]

    Returns
    -------
    np.array
    """
    # A very similar proceedure to the border mask calculations, but we start
    # with ones and create zeros, rather than starting with zeros and creating
    # ones

    # this is the basis of our mask, let everything through
    mask = np.ones(shape=shape)
    # and change the intended pixels to 0
    mask[shield_start[0]:shield_end[0] + 1, shield_start[1]:shield_end[1] + 1] = 0 

    return mask

def get_mask_shape_border(
        shape: tuple[int, int],
        width: int
) -> np.array:
    """Defines a binary matrix representing where the light shield is not
    present along the edges of the array. 
    
    0 represents light shield over that pixel.
    1 represents no light shield over that pixel.
    
    Parameters
    ----------
    shape: tuple[int, int]
    width: int

    Returns
    -------
    np.array
    """
    # define an array the same size as the image full of zeros
    mask = np.zeros(shape=shape)
    mask[width:-width, width:-width] = 1 # and change the middle ones to 1

    # the "middle" ones here is defined as pixels that are `width` amount away
    # from the edges. This gives an array that contains a 1 wherever light 
    # should be untouched, and a 0 where the light shield is. We can multiply
    # this with our photon array to basically remove all light behind this mask

    return mask   


def shield_border(
        detector: Detector,
        width: int
) -> None:
    """Add a light shield all around the image `width` pixels wide/deep.

    Parameters
    ----------
    detector: Detector
    width: int

    Returns
    -------
    None
    """

    photon = detector.photon.array
    mask = get_mask_shape_border(photon.shape, width)

    # our mask contains zeros where there should be no light and ones where the
    # light should be untouched
    detector.photon.array = photon * mask

def shield_box(
        detector: Detector,
        shield_start: tuple[int, int],
        shield_end: tuple[int, int]
) -> None:
    """Add a light shield box from shield_start to shield_end (inclusive).

    Parameters
    ----------
    detector: Detector
    shield_start: tuple[int, int]
    shield_end: tuple[int, int]

    Returns
    -------
    None
    """

    photon = detector.photon.array
    mask = get_mask_shape_box(photon.shape, shield_start, shield_end)

    # our mask contains zeros where there should be no light and ones where the
    # light should be untouched
    detector.photon.array = photon * mask


    