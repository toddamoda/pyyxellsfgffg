#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel charge injection functions for CCDs."""

import numpy as np
import pyxel
# from pyxel.detectors.detector import Detector
from pyxel.detectors.ccd import CCD
# import esapy_config as om


@pyxel.register('charge_generation', name='charge_injection')
def charge_injection(detector: CCD,
                     input_data_list: str = None
                     ) -> CCD:
    """TBW.

    :param detector:
    :param input_data_list: path to (list of) 1d np.arrays
    :return:
    """
    new_detector = detector
    injected_profiles = []
    # # read data from files and create     # TODO
    # for i in range(len(input_data_list)):
    #     rows, _ = input_data_list[i].shape
    #     injected_profiles += [create_injection_profile_highest(input_data_list[i])]
    #     # injected_profiles += [create_injection_profile_average(input_data_list[i])]
    new_detector.charge_injection_profile = injected_profiles
    return new_detector


def create_injection_profile_average(array):
    """TBW.

    :param array:
    :return:
    """
    # # TODO
    # rows, _ = array.shape
    # out = np.zeros(rows)
    # out[np.where(array > threshold)[0]] = np.average(array[40:50])
    # return out.reshape(rows, 1)

    out = np.zeros(2051)
    signal = np.average(array[40:50])
    out[52:102] = signal
    out[552:602] = signal
    out[1052:1102] = signal
    return out.reshape(len(out), 1)


def create_injection_profile_highest(array):
    """TBW.

    :param array:
    :return:
    """
    out = np.zeros(2051)
    signal = np.max(array[0:50])
    out[52:102] = signal
    out[552:602] = signal
    out[1052:1102] = signal
    return out.reshape(len(out), 1)
