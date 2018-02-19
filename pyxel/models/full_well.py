#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""PyXel! CCD full well models."""
# import copy

from pyxel.detectors.detector import Detector


def simple_pixel_full_well(detector: Detector,
                           fwc: int = None) -> Detector:
    """Simply removing charges from pixels due to full well.

    :return:
    """

    # new_detector = copy.deepcopy(detector)
    new_detector = detector

    if fwc is None:
        fwc = new_detector.characteristics.fwc

    charge_array = new_detector.pixels.generate_2d_charge_array()

    mask = charge_array > fwc
    charge_array[mask] = fwc

    new_detector.pixels.update_from_2d_charge_array(charge_array)

    return new_detector


# def mc_full_well(detector: CCD,
#                  fwc: np.ndarray = None) -> CCD:
#     """
#     Moving charges to random neighbour pixels due to full well which depends on pixel location
#     :return:
#     """
#
#     # new_detector = copy.deepcopy(detector)
#     new_detector =detector
#
#     # detector.charges
#
#     # pix_rows = new_detector.pixels.get_pixel_positions_ver()
#     # pix_cols = new_detector.pixels.get_pixel_positions_hor()
#     #
#     # charge = np.zeros((new_detector.row, new_detector.col), dtype=float)
#     # charge[pix_rows, pix_cols] = new_detector.pixels.get_pixel_charges()
#
#     return new_detector
