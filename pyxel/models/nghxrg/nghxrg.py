#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! wrapper class for NGHXRG - Teledyne HxRG Noise Generator model
"""
# import logging
import copy
import numpy as np
from pyxel.detectors.cmos import CMOS

from pyxel.models.nghxrg.nghxrg_beta import HXRGNoise


def run_nghxrg(detector: CMOS,
               rd_noise: float,
               c_pink: float,
               u_pink: float,
               acn: float,
               pca0_amp: float) -> CMOS:

    new_detector = copy.deepcopy(detector)

    ng_h2rg = HXRGNoise(naxis1=new_detector.col, naxis2=new_detector.row, naxis3=1,
                        n_out=4,    # TODO
                        # dt=None,   # TODO
                        # nroh=None, nfoh=None,      # TODO
                        # pca0_file=None,
                        # reverse_scan_direction=False,
                        # reference_pixel_border_width=None,
                        # wind_mode='FULL',
                        # x0=0, y0=0,
                        # det_size=100,
                        verbose=True)

    result = ng_h2rg.add_ktc_bias_noise()   # ktc_noise=None, bias_offset=None, bias_amp=None)
    result += ng_h2rg.add_white_read_noise(rd_noise=rd_noise)   # , reference_pixel_noise_ratio=None)
    result += ng_h2rg.add_corr_pink_noise(c_pink=c_pink)
    result += ng_h2rg.add_uncorr_pink_noise(u_pink=u_pink)
    result += ng_h2rg.add_acn_noise(acn=acn)
    result += ng_h2rg.add_pca_zero_noise(pca0_amp=pca0_amp)

    result = ng_h2rg.format_result(result)

    result = np.rint(result).astype(int)
    # if we add this to the signal(V) then it should be float otherwise int

    new_detector.signal += result   # TODO: Use new_detector.signal OR new_detector.image ?

    ng_h2rg.create_hdu(result, 'pyxel/hxrg_noise.fits')

    return new_detector
