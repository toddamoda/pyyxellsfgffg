"""Pyxel photon generator models."""
import logging
import typing as t
import numpy as np
import pyxel
from pyxel import check_type, check_choices
from pyxel.detectors.detector import Detector


@pyxel.validate
@pyxel.argument(name='level', label='number of photon', units='', validate=check_type(int))
@pyxel.argument(name='option', label='type of illumination', units='',
                validate=check_choices(['uniform', 'rectangular_hole', 'elliptic_hole']))
# @pyxel.argument(name='size', label='size of 2d array', units='', validate=check_type(list))
# @pyxel.argument(name='hole_size', label='size of hole', units='', validate=check_type(list))
def illumination(detector: Detector,
                 level: int,
                 option: str = 'uniform',
                 array_size: t.List[int] = None,
                 hole_size: t.List[int] = None,
                 hole_center: t.List[int] = None):
    """Generate photon uniformly over the entire array or hole.

    detector: Detector
        Pyxel Detector object.
    level: int
        Number of photon per pixel.
    option: str{'uniform', 'elliptic_hole', 'rectangular_hole'}
        A string indicating the type of illumination:

        - ``uniform``
           Uniformly fill the entire array with photon. (Default)
        - ``elliptic_hole``
           Mask with elliptic hole.
        - ``rectangular_hole``
           Mask with rectangular hole.
    array_size: list, optional
        List of integers defining the size of 2d photon array.
    hole_size: list, optional
        List of integers defining the sizes of the elliptic or rectangular hole.
    hole_center: list, optional
        List of integers defining the center of the elliptic or rectangular hole.
    """
    logger = logging.getLogger('pyxel')
    logger.info('')

    if array_size is None:
        try:
            shape = detector.photon.array.shape
        except AttributeError:
            geo = detector.geometry
            detector.photon.new_array(np.zeros((geo.row, geo.col), dtype=int))
            shape = detector.photon.array.shape
    else:
        shape = tuple(array_size)

    if option == 'uniform':
        photon_array = np.ones(shape, dtype=int) * level

    elif option == 'rectangular_hole':
        if hole_size:
            photon_array = np.zeros(shape, dtype=int)
            a = int((shape[0]-hole_size[0]) / 2)
            b = int((shape[1]-hole_size[1]) / 2)
            photon_array[slice(a, a + hole_size[0]), slice(b, b + hole_size[1])] = level
        else:
            raise ValueError('hole_size argument should be defined for illumination model')

    elif option == 'elliptic_hole':
        if hole_size:
            photon_array = np.zeros(shape, dtype=int)
            if hole_center is None:
                hole_center = [int(shape[0] / 2), int(shape[1] / 2)]
            y, x = np.ogrid[:shape[0], :shape[1]]
            dist_from_center = np.sqrt(((x - hole_center[1]) / hole_size[1]) ** 2 +
                                       ((y - hole_center[0]) / hole_size[0]) ** 2)
            photon_array[dist_from_center < 1] = level
        else:
            raise ValueError('hole_size argument should be defined for illumination model')

    else:
        raise NotImplementedError

    try:
        detector.photon.array += photon_array
    except TypeError:
        detector.photon.new_array(photon_array)
    except ValueError:
        raise ValueError('Shapes of arrays do not match')
