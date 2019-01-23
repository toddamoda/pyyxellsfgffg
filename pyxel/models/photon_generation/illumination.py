"""Pyxel photon generator models."""
import logging
import numpy as np
import typing as t
import pyxel
from pyxel import check_type, check_choices
from pyxel.detectors.detector import Detector


@pyxel.validate
@pyxel.argument(name='level', label='number of photons', units='', validate=check_type(int))
@pyxel.argument(name='option', label='type of illumination', units='',
                validate=check_choices(['uniform', 'rectangular_mask', 'elliptic_mask']))
# @pyxel.argument(name='size', label='size of 2d array', units='', validate=check_type(list))
# @pyxel.argument(name='mask_size', label='size of mask', units='', validate=check_type(list))
def illumination(detector: Detector,
                 level: int,
                 option: str = 'uniform',   # todo: remove default arg.
                 size: list = None,
                 mask_size: t.List[int] = None):
    """Generate photons (uniform illumination).

    :param detector: Pyxel Detector object
    :param level: number of photons per pixel, int
    :param size: size of 2d photon array (optional)
    :param option: ``uniform``, ``mask``
    :param mask_size: size of rectangular shaped mask
    """
    logging.info('')

    if size is None:
        try:
            shape = detector.photons.array.shape
        except AttributeError:
            geo = detector.geometry
            detector.photons.new_array(np.zeros((geo.row, geo.col), dtype=int))
            shape = detector.photons.array.shape
    else:
        shape = tuple(size)

    if option == 'uniform':
        photon_array = np.ones(shape, dtype=int) * level
    elif option == 'rectangular_mask':
        if mask_size:
            photon_array = np.zeros(shape, dtype=int)
            a = int((shape[0]-mask_size[0]) / 2)
            b = int((shape[1]-mask_size[1]) / 2)
            photon_array[slice(a, a + mask_size[0]), slice(b, b + mask_size[1])] = level
        else:
            raise ValueError('mask_size argument should be defined for illumination model')
    elif option == 'elliptic_mask':
        if mask_size:
            photon_array = np.zeros(shape, dtype=int)
            h = shape[0]                # TODO
            w = shape[1]                # TODO
            center = None               # TODO
            radius = mask_size[0]       # TODO
            if center is None:  # use the middle of the image
                center = [int(w / 2), int(h / 2)]
            if radius is None:  # use the smallest distance between the center and image walls
                radius = min(center[0], center[1], w - center[0], h - center[1])
            y, x = np.ogrid[:h, :w]
            dist_from_center = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
            photon_array[dist_from_center <= radius] = level
        else:
            raise ValueError('mask_size argument should be defined for illumination model')
    else:
        raise NotImplementedError

    try:
        detector.photons.array += photon_array
    except TypeError:
        detector.photons.new_array(photon_array)
    except ValueError:
        raise ValueError('Shapes of arrays do not match')
