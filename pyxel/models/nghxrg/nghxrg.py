#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! wrapper class for NGHXRG - Teledyne HxRG Noise Generator model
"""
# import logging
import copy

from pyxel.detectors.cmos import CMOS

from pyxel.models.nghxrg.nghxrg_beta import HXRGNoise


def run_nghxrg(detector: CMOS,
               rd_noise: float,
               c_pink: float,
               u_pink: float,
               acn: float,
               pca0_amp: float
               ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    ng_h2rg = HXRGNoise(verbose=True)

    my_hdu = ng_h2rg.mknoise('ex_2.1.1.fits', rd_noise=rd_noise, c_pink=c_pink,
                             u_pink=u_pink, acn=acn, pca0_amp=pca0_amp)

    # new_detector.signal += my_hdu     # TODO: Use new_detector.signal OR new_detector.image ?
    return new_detector
