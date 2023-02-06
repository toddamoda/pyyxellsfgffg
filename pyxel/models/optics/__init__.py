#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import warnings

warnings.warn(
    "Group 'optics' is deprecated "
    "and will be removed in version 2.0. "
    "Use group 'photon_collection' instead.",
    DeprecationWarning,
)

# flake8: noqa
from .poppy import optical_psf
from .point_spread_function import load_psf
