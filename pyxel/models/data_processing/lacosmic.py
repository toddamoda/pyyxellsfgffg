#   Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Remove cosmic rays from an astronomical image using the LA Cosmic algorithm."""
import lacosmic
import numpy as np

from pyxel.detectors import Detector


def remove_cosmic_rays(
    detector: Detector,
    contrast: float = 1.0,
    cr_threshold: float = 50.0,
    neighbor_threshold: float = 50.0,
    effective_gain: float = 1.0,
    readnoise: float = 0.0,
) -> None:
    """Extract the roi data converts it to xarray dataset and saves the information to the final result.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    contrast : float
        todo
    cr_threshold : float
        todo
    neighbor_threshold : float
        todo
    effective_gain : float
        todo
    readnoise : float
        todo
    """
    data_2d = detector.pixel.array
    cleaned_image, cr_mask = lacosmic.lacosmic(
        data_2d,
        contrast=contrast,
        cr_threshold=cr_threshold,
        neighbor_threshold=neighbor_threshold,
        effective_gain=effective_gain,
        readnoise=readnoise,
    )

    # objects, segmap = sep.extract(
    #     data_2d, thresh=thresh, minarea=minarea, segmentation_map=True
    # )
    #
    # ds_objects: xr.Dataset = pd.DataFrame(objects).to_xarray()
    #
    # num_y, num_x = segmap.shape
    #
    # ds_segmap = xr.Dataset()
    # ds_segmap["segmap"] = xr.DataArray(
    #     segmap,
    #     dims=["image_y", "image_x"],
    #     coords={"image_y": range(num_y), "image_x": range(num_x)},
    # )
    #
    # ds = ds_objects.assign_coords(image_y=range(num_y), image_x=range(num_x)).merge(
    #     ds_segmap
    # )
    #
    # detector.processed_data.append(ds)
