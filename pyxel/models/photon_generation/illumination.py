"""Pyxel photon generator models."""
import logging
import numpy as np
import pyxel
from pyxel import check_type, check_choices
from pyxel.detectors.detector import Detector


@pyxel.validate
@pyxel.argument(name='level', label='number of photons', units='', validate=check_type(int))
@pyxel.argument(name='option', label='type of illumination', units='', validate=check_choices(['uniform']))
# @pyxel.argument(name='size', label='size of 2d array', units='', validate=check_type(list))
def illumination(detector: Detector,
                 level: int,
                 option: str = 'uniform',   # todo: remove default arg.
                 size: list = None):
    """Generate photons (uniform illumination).

    :param detector: Pyxel Detector object
    :param level: number of photons per pixel, int
    :param size: size of 2d photon array (optional)
    :param option: ``uniform``
    """
    logging.info('')

    if size is None:
        try:
            size = detector.photons.array.shape
        except AttributeError:
            geo = detector.geometry
            detector.photons.new_array(np.zeros((geo.row, geo.col), dtype=int))
            size = detector.photons.array.shape
    else:
        size = tuple(size)

    if option == 'uniform':
        photon_array = np.ones(size, dtype=int) * level
    else:
        raise NotImplementedError

    try:
        detector.photons.array += photon_array
    except TypeError:
        detector.photons.new_array(photon_array)
    except ValueError:
        raise ValueError('Shapes of arrays do not match')
