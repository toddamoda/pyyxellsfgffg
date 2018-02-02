#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""
PyXel! wrapper class for NGHXRG - Teledyne HxRG Noise Generator model
"""
# import logging
import copy
from os import path
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


def white_read_noise(detector: CMOS,
                     rd_noise: float = None,
                     ref_pixel_noise_ratio: float = None,
                     # window_mode: str = 'FULL',
                     window_mode: str = 'WINDOW',
                     x0: int = 0,
                     y0: int = 0,
                     wind_x_size: int = 4,
                     wind_y_size: int = 4
                     ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    # TODO need another det_size parameter, then this can be deleted
    # check whether detector has a square shape:
    det_size = 0
    if new_detector.col == new_detector.row:
        det_size = new_detector.col  # TODO modify det_size in HXRGNoise class
    else:
        NotImplemented()

    # TODO move these into a function
    naxis3 = 1
    if window_mode == 'FULL':         # this works with different x and y array sizes
        naxis1 = new_detector.col     # * 2
        naxis2 = new_detector.row
    elif window_mode == 'WINDOW':     # TODO: BUG - code doesn't work with different x and y array sizes
        naxis1 = wind_x_size
        naxis2 = wind_y_size
    else:
        raise ValueError()

    ng_h2rg = HXRGNoise(naxis1=naxis1, naxis2=naxis2, naxis3=naxis3,
                        n_out=new_detector.n_output,
                        nroh=new_detector.n_row_overhead,
                        nfoh=new_detector.n_frame_overhead,
                        reverse_scan_direction=new_detector.reverse_scan_direction,
                        reference_pixel_border_width=new_detector.reference_pixel_border_width,
                        pca0_file=path.dirname(path.abspath(__file__)) + '/nirspec_pca0.fits',
                        det_size=det_size,
                        wind_mode=window_mode,
                        x0=x0, y0=y0,
                        verbose=True)

    result = ng_h2rg.add_white_read_noise(rd_noise=rd_noise, reference_pixel_noise_ratio=ref_pixel_noise_ratio)

    result = ng_h2rg.format_result(result)

    # new_detector.signal += result
    # TODO: add to new_detector.signal OR new_detector.image OR charge dataframe ?
    # TODO: if result array smaller than signal array ('WINDOW' mode), then find x0,y0 position and add to it there

    ng_h2rg.create_hdu(result, 'pyxel/hxrg_read_noise.fits')

    return new_detector
