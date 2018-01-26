#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! wrapper class for NGHXRG - Teledyne HxRG Noise Generator model 
"""
# import logging
import copy

from pyxel.detectors.cmos import CMOS

from pyxel.models.nghxrg.nghxrg_v2_6beta import HXRGNoise


def run_nghxrg_v26beta(detector: CMOS) -> CMOS:

    new_detector = copy.deepcopy(detector)

    ng_h2rg = HXRGNoise(verbose=True)

    # Use parameters that generate noise similar to JWST NIRSpec
    rd_noise = 4.  # White read noise per integration
    pedestal = 4.  # DC pedestal drift rms
    c_pink = 3.  # Correlated pink noise
    u_pink = 1.  # Uncorrelated pink noise
    acn = .5  # Correlated ACN
    pca0_amp = .2  # Amplitude of PCA zero "picture frame" noise

    # Do it
    my_hdu = ng_h2rg.mknoise('ex_2.1.1.fits', rd_noise=rd_noise, pedestal=pedestal,
                             c_pink=c_pink, u_pink=u_pink, acn=acn, pca0_amp=pca0_amp)

    return new_detector
