# Copyright or © or Copr. Antoine Kaszczyc and Aurelien Jarno, Centre de Recherche Astrophysique de Lyon (CRAL)  (2025)
#
# Antoine Kaszczyc <antoine.kaszczyc@univ-lyon1.fr>
# Aurelien Jarno <aurelien.jarno@univ-lyon1.fr>
#
# This file is part of the Pyxel general simulator framework.
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

"""Readout noise model."""

import numpy as np
from astropy.units import Quantity

from pyxel.detectors import CMOS
from pyxel.detectors.channels import Channels
from pyxel.util import PinkNoiseGenerator


# this function is used both for generating pink noise for one channel,
# as well as generating pink noise for full detector (the "no channels" case)
def create_pink_noise_cmos(
    nb_pixels_overhead_after_row: int,
    nb_rows_overhead_after_frame: int,
    generator: PinkNoiseGenerator,
    shape: tuple[int, int],
    std: Quantity,  # electron
):  # electron
    """Create a matrix of pink noise, using given generator.

    rows and frame overhead reads are taken into account. Generated pink noise has
    standard deviation equal to `1`, we then multiply it by parameter `std`.
    """
    assert std.unit == "electron"
    (nb_rows, nb_cols) = shape
    # we generate one pink noise value for every pixel read,
    # but we also generate "overhead" reads, that physically happen
    # these overhead reads will be discarded afterwards, but because
    # this is pink noise, we must simulate them
    nb_pixel_reads = (nb_rows + nb_rows_overhead_after_frame) * (
        nb_cols + nb_pixels_overhead_after_row
    )
    pink_noise = generator.get(nb_pixel_reads)
    # reshape, so that non-overhead reads are grouped into a rectangle
    noise_2d = pink_noise.reshape(
        (nb_rows + nb_rows_overhead_after_frame),
        (nb_cols + nb_pixels_overhead_after_row),
    )
    # select all "non-overhead" reads
    noise_2d = noise_2d[0:nb_rows, 0:nb_cols]
    noise_2d = Quantity(noise_2d, unit="electron")
    noise_2d *= std.value
    return noise_2d


def create_uncorrelated_pink_noise_cmos_by_chan(
    channels: Channels,
    nb_pixels_overhead_after_row: int,
    nb_rows_overhead_after_frame: int,
    generator_by_chan: dict[str, PinkNoiseGenerator],
    detector_shape: tuple[int, int],
    std_by_chan: dict[str, Quantity],
) -> np.ndarray:
    """Create a matrix with uncorrelated pink noise to each channel.

    Each channel has its own generator, and readout pixel order is respected.
    """

    noise_2d = np.zeros(detector_shape)
    for chan_label in list(channels):
        # construct a view on `noise_2d`, with every pixel belonging to
        # this channel, with respect to readout order
        this_chan_view = noise_2d[
            channels.get_channel_slices(detector_shape, chan_label)
        ]
        # generate pink noise for this channel and fill it inside the view
        this_chan_view[:, :] = create_pink_noise_cmos(
            nb_pixels_overhead_after_row,
            nb_rows_overhead_after_frame,
            generator=generator_by_chan[chan_label],
            shape=this_chan_view.shape,
            std=std_by_chan[chan_label],
        )
    return Quantity(noise_2d, unit="electron")


def uncorrelated_pink_noise_cmos(
    detector: CMOS,
    nb_pixels_overhead_after_row: int = 0,
    nb_rows_overhead_after_frame: int = 0,
    std: float | dict[str, float] = 1.0,
    seed: int | None = None,
) -> None:
    """Add Uncorrelated pink noise into `pixel.volatile` array.

    For uncorrelated pink noise, each channel has its own generator. The noise is
    read order dependent, and some overhead reads are simulated. Generators states
    are stored inside `CMOS` (`Detector`) object.

    Parameters
    ----------
    detector : CMOS
    nb_pixels_overhead_after_row : int, optional
        Number of overhead pixels to simulate after each row read.
        Used to advance the pink-noise generators consistently.
        Default is ``0``.
    nb_rows_overhead_after_frame : int, optional
        Number of overhead rows to simulate after each frame read.
        Default is ``0``.
    std : float or dict of float, optional
        Standard deviation of the pink noise in electrons:
          - If a scalar is provided, it is applied identically to all channels.
          - If a dictionary is provided, keys must match channel labels defined in ``detector.geometry.channels``.

        All provided values must be positive. Default is ``1.0``.
    seed : int or None, optional
        Random seed used for initializing the pink-noise generators.
        Only applied during the first invocation. Default is ``None``.
    """
    # init the pink noise generators with the seed (only the first time)
    try:
        _ = detector.uncorrelated_pink_noise_generators
    except RuntimeError:
        detector.set_uncorrelated_pink_noise_generators(seed)

    if detector.geometry.channels:
        ##########################################
        # channels                               #
        ##########################################

        # construct a dict to store one `std` for each channel
        # keys are channels labels
        # if user gave a scalar for `std` parameter, this scalar is
        # copied for every channel
        std_by_chan = dict()
        for chan_label in list(detector.geometry.channels):
            st = std if isinstance(std, (int, float)) else std[chan_label]
            if st < 0.0:
                raise ValueError("'std' must be positive.")
            std_by_chan[chan_label] = Quantity(st, unit="electron")

        # fill each channel with pink noise
        noise_2d = create_uncorrelated_pink_noise_cmos_by_chan(
            detector.geometry.channels,
            nb_pixels_overhead_after_row,
            nb_rows_overhead_after_frame,
            generator_by_chan=detector.uncorrelated_pink_noise_generators,
            detector_shape=detector.geometry.shape,
            std_by_chan=std_by_chan,
        )

    else:
        ##########################################
        # no channels                            #
        ##########################################
        if isinstance(std, dict):
            raise ValueError(
                "Per-channel noise parameter was provided, but the detector "
                "does not define any geometry channels."
            )

        # fill whole detector with pink noise from the one generator
        noise_2d = create_pink_noise_cmos(
            nb_pixels_overhead_after_row,
            nb_rows_overhead_after_frame,
            generator=detector.uncorrelated_pink_noise_generators["default"],
            shape=detector.geometry.shape,
            std=Quantity(std, unit="electron"),
        )

    # pink noise do not accumulate in the pixel wells,
    # so we put it in `volatile`
    detector.pixel.volatile += noise_2d
