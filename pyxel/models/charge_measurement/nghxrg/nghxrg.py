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
            noise_name = 'ktc_bias_noise'
            if item['ktc_bias_noise']:
                result = ng.add_ktc_bias_noise(ktc_noise=item['ktc_noise'],
                                               bias_offset=item['bias_offset'],
                                               bias_amp=item['bias_amp'])
        elif 'white_read_noise' in item:
            noise_name = 'white_read_noise'
            if item['white_read_noise']:
                result = ng.add_white_read_noise(rd_noise=item['rd_noise'],
                                                 reference_pixel_noise_ratio=item['ref_pixel_noise_ratio'])
        elif 'corr_pink_noise' in item:
            noise_name = 'corr_pink_noise'
            if item['corr_pink_noise']:
                result = ng.add_corr_pink_noise(c_pink=item['c_pink'])
        elif 'uncorr_pink_noise' in item:
            noise_name = 'uncorr_pink_noise'
            if item['uncorr_pink_noise']:
                result = ng.add_uncorr_pink_noise(u_pink=item['u_pink'])
        elif 'acn_noise' in item:
            noise_name = 'acn_noise'
            if item['acn_noise']:
                result = ng.add_acn_noise(acn=item['acn'])
        elif 'pca_zero_noise' in item:
            noise_name = 'pca_zero_noise'
            if item['pca_zero_noise']:
                result = ng.add_pca_zero_noise(pca0_amp=item['pca0_amp'])   # TODO : pca0_file=item['pca0_file'])

        try:
            result = ng.format_result(result)
            if window_mode == 'FULL':
                display_noisepsd(result, geo.n_output, (geo.col, geo.row), noise_name)
                detector.pixel.array += result
            elif window_mode == 'WINDOW':
                detector.pixel.array[wind_y0:wind_y0 + wind_y_size, wind_x0:wind_x0 + wind_x_size] += result
        except TypeError:
            pass

def display_noisepsd(array, nb_output, dimension, noise_name, mode='plot'):
    ''' Method to display noise PSD from the generated FITS file
    ''' 
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import signal
    ## Conversion gain
    conversion_gain = 1
    data_corr = array * conversion_gain

    '''
    For power spectra, need to be careful of readout directions

    For the periodogram, using Welch's method to smooth the PSD
    > Divide data in N segment of length nperseg which overlaps at nperseg/2 (noverlap argument)
    nperseg high means less averaging for the PSD but more points
    '''

    ## Should be in the simulated data header
    dimension = dimension[0]
    pix_p_output = dimension**2 / nb_output # Number of pixels per output
    nbcols_p_channel = dimension / nb_output # Number of columns per channel 
    nperseg = int(pix_p_output / 10.) # Length of segments for Welch's method
    read_freq = 100000 # Frame rate [Hz]

    ## Initializing table of nb_outputs periodogram
    Pxx_outputs = np.zeros((nb_output,int(nperseg/2)+1)) # +1 for periodogram dimensions

    ## For each output
    for i in np.arange(nb_output):
        # If i odd, flatten data since its the good reading direction
        if i%2 == 0:
            output_data = data_corr[:,int(i*(nbcols_p_channel)):int((i+1)*(nbcols_p_channel))].flatten()
        # Else, flip it left/right and then flatten it
        else:
            output_data = np.fliplr(data_corr[:,int(i*(nbcols_p_channel)):int((i+1)*(nbcols_p_channel))]).flatten()    
        # output data without flipping
        #output_data = data_corr[:,int(i*(nbcols_p_channel)):int((i+1)*(nbcols_p_channel))].flatten()

        ## Add periodogram to the previously initialized array 
        f_vect, Pxx_outputs[i] = signal.welch(output_data, read_freq, nperseg=nperseg)

    ## For the detector
    #detector_data = data_corr.flatten()    
    ## Add periodogram to the previously initialized array 
    # test, Pxx_detector = signal.welch(detector_data, read_freq, nperseg=nperseg)     
    
    if mode == 'plot':
        ## Plotting
        fig, ax1 = plt.subplots(1,1,figsize=(8,8))
        fig.canvas.set_window_title('Power Spectral Density')
        fig.suptitle(noise_name.capitalize()+' Power Spectral Density [PSD]\n\
        Welch seg. length / Nb pixel output: '+str('{:1.2f}'.format(nperseg/pix_p_output)))#+')\n\
        #File: '+datafile)
        ax1.plot(f_vect,np.mean(Pxx_outputs,axis=0),'.-',ms=3,alpha=0.3,label='PSD outputs',zorder=32)
        for idx, ax in enumerate([ax1]):
            ax.set_xlim([1, 1e5])
            #ax.set_ylim([1e-5, 1e0])
            ax.set_xscale('log')
            ax.set_yscale('log')
            #if idx != 0:
            ax.set_xlabel('Frequency [Hz]')
            ax.set_ylabel('PSD [e-${}^2$/Hz]')
            ax.legend(fontsize=12)
            ax.grid(True,alpha=.4)
        plt.savefig('outputs/'+noise_name.capitalize()+'.png')
    
    return f_vect,np.mean(Pxx_outputs,axis=0)