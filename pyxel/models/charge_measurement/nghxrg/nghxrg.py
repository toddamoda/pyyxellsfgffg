#   --------------------------------------------------------------------------
#   Copyright 2018 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
"""Pyxel wrapper class for NGHXRG - Teledyne HxRG Noise Generator model."""

import logging
# import pyxel
from pyxel.detectors.cmos import CMOS
from pyxel.models.charge_measurement.nghxrg.nghxrg_beta import HXRGNoise


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def nghxrg(detector: CMOS,
           noise: list,
           window_mode: str = 'FULL',
           wind_x0: int = 0, wind_y0: int = 0,
           wind_x_size: int = 0, wind_y_size: int = 0):
    """TBW.

    :param detector: Pyxel Detector object
    :param noise:
    :param window_mode:
    :param wind_x0:
    :param wind_y0:
    :param wind_x_size:
    :param wind_y_size:
    """
    logging.getLogger("nghxrg").setLevel(logging.WARNING)
    logger = logging.getLogger('pyxel')
    logger.info('')
    geo = detector.get_geometry()
    number_of_fits = 1
    ng = HXRGNoise(n_out=geo.n_output,
                   nroh=geo.n_row_overhead,
                   nfoh=geo.n_frame_overhead,
                   reverse_scan_direction=geo.reverse_scan_direction,
                   reference_pixel_border_width=geo.reference_pixel_border_width,
                   # pca0_file=,    # TODO
                   det_size_x=geo.col, det_size_y=geo.row,
                   wind_mode=window_mode,
                   wind_x_size=wind_x_size, wind_y_size=wind_y_size,
                   wind_x0=wind_x0, wind_y0=wind_y0,
                   cube_z=number_of_fits,
                   verbose=True)

    for item in noise:
        result = None
        if 'ktc_bias_noise' in item:
            if item['ktc_bias_noise']:
                result = ng.add_ktc_bias_noise(ktc_noise=item['ktc_noise'],
                                               bias_offset=item['bias_offset'],
                                               bias_amp=item['bias_amp'])
        elif 'white_read_noise' in item:
            if item['white_read_noise']:
                result = ng.add_white_read_noise(rd_noise=item['rd_noise'],
                                                 reference_pixel_noise_ratio=item['ref_pixel_noise_ratio'])
        elif 'corr_pink_noise' in item:
            if item['corr_pink_noise']:
                result = ng.add_corr_pink_noise(c_pink=item['c_pink'])
        elif 'uncorr_pink_noise' in item:
            if item['uncorr_pink_noise']:
                result = ng.add_uncorr_pink_noise(u_pink=item['u_pink'])
        elif 'acn_noise' in item:
            if item['acn_noise']:
                result = ng.add_acn_noise(acn=item['acn'])
        elif 'pca_zero_noise' in item:
            if item['pca_zero_noise']:
                result = ng.add_pca_zero_noise(pca0_amp=item['pca0_amp'])   # TODO : pca0_file=item['pca0_file'])

        try:
            result = ng.format_result(result)
            if window_mode == 'FULL':
                detector.pixel.array += result
            elif window_mode == 'WINDOW':
                detector.pixel.array[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
        except TypeError:
            pass
