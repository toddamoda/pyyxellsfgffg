#   --------------------------------------------------------------------------
#   Copyright 2017 SCI-FIV, ESA (European Space Agency)
#   --------------------------------------------------------------------------
""" PyXel! - Photon Transfer Curve

Calling pyxel_alpha with different uniform photon average number as an input to generate data file
and plotting Photon Transfer Curve from data file, fitting linear to noise on log scale
"""

# import matplotlib.pyplot as plt
# import numpy as np
# import pyxel

# FIT_READ = False
# FIT_SHOT = False
# FIT_FIX = False
# GENERATE_DATA = False


def main():
    """ main entry point of script. """

    # if GENERATE_DATA:
    #     for i in np.logspace(2.0, 4.0, 200, dtype=int):
    #         pyxel_alpha.main()

    # Plotting Photon Transfer Curve data
    # data = np.loadtxt(r'C:\dev\work\pyxel\data\output.data')
    #
    # # x_photons = data[1:, 0].flatten()    # mean photon
    # x_signal = data[1:, 1].flatten()    # mean signal
    # y_sigma = data[1:, 2].flatten()    # st. deviation
    #
    # fig = plt.figure()
    # plt.plot(x_signal, y_sigma, 'g.')
    #
    # fig.suptitle(r'PyXel $\alpha$', fontsize=14, fontweight='bold')
    # ax = plt.gca()
    # ax.set_title('CCD Photon Transfer Curve')
    # ax.set_xlabel('Signal mean (DN)')
    # ax.set_ylabel('Noise (DN)')
    # ax.set_xscale('log')
    # ax.set_yscale('log')
    # xul, yul = 1E+5, 3E+3
    # ax.set_xlim(1E+0, xul)
    # ax.set_ylim(1E+0, yul)
    #
    # # FITTING
    # if FIT_SHOT or FIT_FIX or FIT_READ:
    #     fig2 = plt.figure()
    #     fig2.suptitle(r'PyXel $\alpha$', fontsize=14, fontweight='bold')
    #     plt.plot(np.log10(x_signal), np.log10(y_sigma), 'g.')
    #
    #     if FIT_READ:
    #         read_fit1 = 1
    #         read_fit2 = np.argmax(y_sigma)-1
    #         # read_fit1 = np.argmax(x_signal > 0)
    #         # read_fit2 = np.argmax(x_signal > 10)
    #         x_read_fit = x_signal[read_fit1:read_fit2]
    #         y_read_fit = y_sigma[read_fit1:read_fit2]
    #         fit_read = np.polyfit(np.log10(x_read_fit), np.log10(y_read_fit), 1)
    #         print('readout noise fit (slope and intercept): ', fit_read)
    #         plt.plot(np.log10(x_signal), fit_read[0] * np.log10(x_signal) + fit_read[1], 'y-', label="readout noise fit")
    #     if FIT_SHOT:
    #         # shot_fit1 = np.argmax(x_signal > 100)
    #         # shot_fit2 = np.argmax(x_signal > 500)
    #         shot_fit1 = 1
    #         shot_fit2 = np.argmax(y_sigma)-1
    #         x_shot_fit = x_signal[shot_fit1:shot_fit2]
    #         y_shot_fit = y_sigma[shot_fit1:shot_fit2]
    #         fit_shot = np.polyfit(np.log10(x_shot_fit), np.log10(y_shot_fit), 1)
    #         print('shot noise fit (slope and intercept): ', fit_shot)
    #         plt.plot(np.log10(x_signal), fit_shot[0] * np.log10(x_signal) + fit_shot[1], 'b-', label="shot noise fit")
    #     if FIT_FIX:
    #         # fix_fit1 = np.argmax(x_signal > 13000)
    #         fix_fit1 = 1
    #         fix_fwc = np.argmax(y_sigma)-1
    #         x_fix_fit = x_signal[fix_fit1:fix_fwc]
    #         y_fix_fit = y_sigma[fix_fit1:fix_fwc]
    #         fit_fix = np.polyfit(np.log10(x_fix_fit), np.log10(y_fix_fit), 1)
    #         print('fix pattern noise fit (slope and intercept): ', fit_fix)
    #         plt.plot(np.log10(x_signal), fit_fix[0] * np.log10(x_signal) + fit_fix[1], 'r-', label="fix pattern noise fit")
    #
    #     ax2 = plt.gca()
    #     ax2.set_title('CCD Photon Transfer Curve')
    #     ax2.set_xlabel('Log Signal mean (DN)')
    #     ax2.set_ylabel('Log Noise (DN)')
    #     ax2.set_xlim(0, np.log10(xul))
    #     ax2.set_ylim(0, np.log10(yul))
    #     plt.legend(loc=2)
    #
    # plt.show()


if __name__ == '__main__':
    main()
