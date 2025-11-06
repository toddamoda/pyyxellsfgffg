#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Top-level import of Pyxel models."""

# flake8: noqa
from .util import load_detector, save_detector

# Photon collection models
from .photon_collection.illumination import illumination
from .photon_collection.load_image import load_image
from .photon_collection.shot_noise import shot_noise
from .photon_collection.stripe_pattern import stripe_pattern
from .photon_collection.poppy import optical_psf
from .photon_collection.point_spread_function import load_psf, load_wavelength_psf
from .photon_collection.ariel_airs import wavelength_dependence_airs
from .photon_collection.simple_collection import simple_collection
from .photon_collection.usaf_illumination import usaf_illumination
from .photon_collection.photon_modulation import photon_flux_modulation

__all__ = [
    "load_detector",
    "save_detector",
    "illumination",
    "load_image",
    "shot_noise",
    "stripe_pattern",
    "optical_psf",
    "load_psf",
    "load_wavelength_psf",
    "wavelength_dependence_airs",
    "simple_collection",
    "usaf_illumination",
    "photon_flux_modulation",
]
