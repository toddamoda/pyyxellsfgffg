#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

<<<<<<< HEAD
"""Photon generation models are used to add to and manipulate data in Photon array
=======
"""Photon generation models are used to add to and manipulate data in the Photon array
>>>>>>> 3100880b (Add load_general_image function with tests and YAML example)
inside the Detector object."""

# flake8: noqa
from .illumination import illumination
<<<<<<< HEAD
from .load_image import load_image
=======
from .load_image import load_image, load_general_image
>>>>>>> 3100880b (Add load_general_image function with tests and YAML example)
from .shot_noise import shot_noise
from .stripe_pattern import stripe_pattern
from .poppy import optical_psf
from .point_spread_function import load_psf, load_wavelength_psf
from .ariel_airs import wavelength_dependence_airs
from .simple_collection import simple_collection
from .usaf_illumination import usaf_illumination
<<<<<<< HEAD
=======

__all__ = [
    "illumination",
    "load_image",
    "load_general_image",
    "shot_noise",
    "stripe_pattern",
    "optical_psf",
    "load_psf",
    "load_wavelength_psf",
    "wavelength_dependence_airs",
    "simple_collection",
    "usaf_illumination",
]
>>>>>>> 3100880b (Add load_general_image function with tests and YAML example)
