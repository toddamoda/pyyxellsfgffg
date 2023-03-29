#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage with all models related to the 'DataProcessing' model group."""

# flake8: noqa
from .statistics import compute_statistics
from .source_extractor import (
    show_detector,
    get_background,
    get_background_image,
    get_background_data,
    subtract_background,
    extract_roi,
    plot_roi,
    extract_roi_to_xarray,
)
