#  Copyright (c) YOUR COPYRIGHT HERE

"""
shield module for the PyXel simulation.

This module is used in photon_collection

-------------------------------------------------------------------------------

+--------------+----------------------------------+---------------------------+
| Author       | Name                             | Creation                  |
+--------------+----------------------------------+---------------------------+
| You          | shield                        | Thu Jul  3 16:21:15 2025                   |
+--------------+----------------------------------+---------------------------+

+-----------------+-------------------------------------+---------------------+
| Contributor     | Name                                | Creation            |
+-----------------+-------------------------------------+---------------------+
| Name            | filename                            | 06/21/2019          |
+-----------------+-------------------------------------+---------------------+

This is a documentation template for the shield module.
This docstring can be used for automatic doc generation and explain more
in detail what the shield module does in PyXel.

This module can be found in pyxel/models/photon_collection.
Please modify the docstrings accordingly to provide the users a simple and
detailed explanation of your algorithm for this module.

Table examples
==============

===============  ==============================================================
Table entries    Table values
===============  ==============================================================
Entry 1          Value 1
Entry 2          Value 2
Entry 3          Value 3

Entry 4          Value 4

Entry 5          Value 5
===============  ==============================================================

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | - Table cells       |
+------------------------+ span rows. | - contain           |
| body row 4             |            | - body elements.    |
+------------------------+------------+----------+----------+
| body row 5             | Cells may also be     |          |
|                        | empty: ``-->``        |          |
+------------------------+-----------------------+----------+

Code example
============

.. code-block:: python

    import sys

    print("Hello world...")


.. literalinclude:: pyxel/models/photon_collection/shield.py
    :language: python
    :linenos:
    :lines: 84-87

Model reference in the YAML config file
=======================================

.. code-block:: yaml

    pipeline:

      # Small comment on what it does
      photon_collection:
        - name: shield
          func: pyxel.models.photon_collection.shield.model
          enabled: true
          arguments:
            arg1: data/fits/Pleiades_HST.fits
            arg2: true
            arg3: 42

Useful links
============

ReadTheDocs documentation
https://sphinx-rtd-theme.readthedocs.io/en/latest/index.html

.. todo::

   Write the documentation for shield

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
    # Do operation on one of those arrays and return None.

    # Done!

    ## detector.photon += 1
    # photon = detector.photon.array
    # photon_2d = detector.photon.array_2d
    # for i in range(0, len(detector.photon.array)):
    #     if i >= shield_start[0] and i <= shield_end[0]:
    #         for j in range(0, len(detector.photon.array[i])):
    #             if j >= shield_start[1] and j <= shield_end[1]:
    #                 photon[i, j] = 0
    #                 photon_2d[i, j] = 0
    #     i = i + 1

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

    # Access the detector
    """
    photon = detector.photon.array
    pixel = detector.pixel.array
    signal = detector.signal.array
    image = detector.image.array
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
    """Add a light shield all around the image `width` pixels wide/deep.

    Parameters
    ----------
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


    