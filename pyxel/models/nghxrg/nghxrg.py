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


def white_read_noise(detector: CMOS,
                     rd_noise: float = None,
                     ref_pixel_noise_ratio: float = None,
                     window_mode: str = 'FULL',
                     wind_x0: int = 0, wind_y0: int = 0,
                     wind_x_size: int = 0, wind_y_size: int = 0
                     ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    number_of_fits = 1

    ng_h2rg = HXRGNoise(n_out=new_detector.n_output,
                        nroh=new_detector.n_row_overhead,
                        nfoh=new_detector.n_frame_overhead,
                        reverse_scan_direction=new_detector.reverse_scan_direction,
                        reference_pixel_border_width=new_detector.reference_pixel_border_width,
                        pca0_file=path.dirname(path.abspath(__file__)) + '/nirspec_pca0.fits',
                        det_size_x=new_detector.col, det_size_y=new_detector.row,
                        wind_mode=window_mode,
                        wind_x_size=wind_x_size, wind_y_size=wind_y_size,
                        wind_x0=wind_x0, wind_y0=wind_y0,
                        cube_z=number_of_fits,
                        verbose=True)

    result = ng_h2rg.add_white_read_noise(rd_noise=rd_noise, reference_pixel_noise_ratio=ref_pixel_noise_ratio)

    result = ng_h2rg.format_result(result)

    if window_mode == 'FULL':
        new_detector.signal += result
    elif window_mode == 'WINDOW':
        new_detector.signal[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
    # TODO: add to new_detector.signal OR new_detector.image OR charge dataframe ?

    # ng_h2rg.create_hdu(result, 'pyxel/hxrg_read_noise.fits')

    return new_detector


def ktc_bias_noise(detector: CMOS,
                   ktc_noise: float = None,
                   bias_offset: float = None,
                   bias_amp: float = None,
                   window_mode: str = 'FULL',
                   wind_x0: int = 0, wind_y0: int = 0,
                   wind_x_size: int = 0, wind_y_size: int = 0
                   ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    number_of_fits = 1

    ng_h2rg = HXRGNoise(n_out=new_detector.n_output,
                        nroh=new_detector.n_row_overhead,
                        nfoh=new_detector.n_frame_overhead,
                        reverse_scan_direction=new_detector.reverse_scan_direction,
                        reference_pixel_border_width=new_detector.reference_pixel_border_width,
                        pca0_file=path.dirname(path.abspath(__file__)) + '/nirspec_pca0.fits',
                        det_size_x=new_detector.col, det_size_y=new_detector.row,
                        wind_mode=window_mode,
                        wind_x_size=wind_x_size, wind_y_size=wind_y_size,
                        wind_x0=wind_x0, wind_y0=wind_y0,
                        cube_z=number_of_fits,
                        verbose=True)

    result = ng_h2rg.add_ktc_bias_noise(ktc_noise=ktc_noise, bias_offset=bias_offset, bias_amp=bias_amp)

    result = ng_h2rg.format_result(result)

    if window_mode == 'FULL':
        new_detector.signal += result
    elif window_mode == 'WINDOW':
        new_detector.signal[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
    # TODO: add to new_detector.signal OR new_detector.image OR charge dataframe ?

    # ng_h2rg.create_hdu(result, 'pyxel/hxrg_read_noise.fits')

    return new_detector


def corr_pink_noise(detector: CMOS,
                    c_pink: float = None,
                    window_mode: str = 'FULL',
                    wind_x0: int = 0, wind_y0: int = 0,
                    wind_x_size: int = 0, wind_y_size: int = 0
                    ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    number_of_fits = 1

    ng_h2rg = HXRGNoise(n_out=new_detector.n_output,
                        nroh=new_detector.n_row_overhead,
                        nfoh=new_detector.n_frame_overhead,
                        reverse_scan_direction=new_detector.reverse_scan_direction,
                        reference_pixel_border_width=new_detector.reference_pixel_border_width,
                        pca0_file=path.dirname(path.abspath(__file__)) + '/nirspec_pca0.fits',
                        det_size_x=new_detector.col, det_size_y=new_detector.row,
                        wind_mode=window_mode,
                        wind_x_size=wind_x_size, wind_y_size=wind_y_size,
                        wind_x0=wind_x0, wind_y0=wind_y0,
                        cube_z=number_of_fits,
                        verbose=True)

    result = ng_h2rg.add_corr_pink_noise(c_pink=c_pink)

    result = ng_h2rg.format_result(result)

    if window_mode == 'FULL':
        new_detector.signal += result
    elif window_mode == 'WINDOW':
        new_detector.signal[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
    # TODO: add to new_detector.signal OR new_detector.image OR charge dataframe ?

    # ng_h2rg.create_hdu(result, 'pyxel/hxrg_read_noise.fits')

    return new_detector


def uncorr_pink_noise(detector: CMOS,
                      u_pink: float = None,
                      window_mode: str = 'FULL',
                      wind_x0: int = 0, wind_y0: int = 0,
                      wind_x_size: int = 0, wind_y_size: int = 0
                      ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    number_of_fits = 1

    ng_h2rg = HXRGNoise(n_out=new_detector.n_output,
                        nroh=new_detector.n_row_overhead,
                        nfoh=new_detector.n_frame_overhead,
                        reverse_scan_direction=new_detector.reverse_scan_direction,
                        reference_pixel_border_width=new_detector.reference_pixel_border_width,
                        pca0_file=path.dirname(path.abspath(__file__)) + '/nirspec_pca0.fits',
                        det_size_x=new_detector.col, det_size_y=new_detector.row,
                        wind_mode=window_mode,
                        wind_x_size=wind_x_size, wind_y_size=wind_y_size,
                        wind_x0=wind_x0, wind_y0=wind_y0,
                        cube_z=number_of_fits,
                        verbose=True)

    result = ng_h2rg.add_uncorr_pink_noise(u_pink=u_pink)

    result = ng_h2rg.format_result(result)

    if window_mode == 'FULL':
        new_detector.signal += result
    elif window_mode == 'WINDOW':
        new_detector.signal[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
    # TODO: add to new_detector.signal OR new_detector.image OR charge dataframe ?

    # ng_h2rg.create_hdu(result, 'pyxel/hxrg_read_noise.fits')

    return new_detector


def acn_noise(detector: CMOS,
              acn: float = None,
              window_mode: str = 'FULL',
              wind_x0: int = 0, wind_y0: int = 0,
              wind_x_size: int = 0, wind_y_size: int = 0
              ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    number_of_fits = 1

    ng_h2rg = HXRGNoise(n_out=new_detector.n_output,
                        nroh=new_detector.n_row_overhead,
                        nfoh=new_detector.n_frame_overhead,
                        reverse_scan_direction=new_detector.reverse_scan_direction,
                        reference_pixel_border_width=new_detector.reference_pixel_border_width,
                        pca0_file=path.dirname(path.abspath(__file__)) + '/nirspec_pca0.fits',
                        det_size_x=new_detector.col, det_size_y=new_detector.row,
                        wind_mode=window_mode,
                        wind_x_size=wind_x_size, wind_y_size=wind_y_size,
                        wind_x0=wind_x0, wind_y0=wind_y0,
                        cube_z=number_of_fits,
                        verbose=True)

    result = ng_h2rg.add_acn_noise(acn=acn)

    result = ng_h2rg.format_result(result)

    if window_mode == 'FULL':
        new_detector.signal += result
    elif window_mode == 'WINDOW':
        new_detector.signal[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
    # TODO: add to new_detector.signal OR new_detector.image OR charge dataframe ?

    # ng_h2rg.create_hdu(result, 'pyxel/hxrg_read_noise.fits')

    return new_detector


def pca_zero_noise(detector: CMOS,
                   pca0_amp: float = None,
                   window_mode: str = 'FULL',
                   wind_x0: int = 0, wind_y0: int = 0,
                   wind_x_size: int = 0, wind_y_size: int = 0
                   ) -> CMOS:

    new_detector = copy.deepcopy(detector)

    number_of_fits = 1

    ng_h2rg = HXRGNoise(n_out=new_detector.n_output,
                        nroh=new_detector.n_row_overhead,
                        nfoh=new_detector.n_frame_overhead,
                        reverse_scan_direction=new_detector.reverse_scan_direction,
                        reference_pixel_border_width=new_detector.reference_pixel_border_width,
                        pca0_file=path.dirname(path.abspath(__file__)) + '/nirspec_pca0.fits',
                        det_size_x=new_detector.col, det_size_y=new_detector.row,
                        wind_mode=window_mode,
                        wind_x_size=wind_x_size, wind_y_size=wind_y_size,
                        wind_x0=wind_x0, wind_y0=wind_y0,
                        cube_z=number_of_fits,
                        verbose=True)

    result = ng_h2rg.add_pca_zero_noise(pca0_amp=pca0_amp)

    result = ng_h2rg.format_result(result)

    if window_mode == 'FULL':
        new_detector.signal += result
    elif window_mode == 'WINDOW':
        new_detector.signal[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
    # TODO: add to new_detector.signal OR new_detector.image OR charge dataframe ?

    # ng_h2rg.create_hdu(result, 'pyxel/hxrg_read_noise.fits')

    return new_detector
