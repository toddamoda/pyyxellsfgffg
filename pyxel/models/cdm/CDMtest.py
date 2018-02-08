import datetime
import os
import typing as t
import numpy as np
from astropy.io import fits as pf
# from matplotlib import pyplot as plt

# from pyxel.models.cdm.CDM import CDM03Python    # as CTI


def testPythonCDM03(parallel='cdm_euclid_parallel.dat',
                    serial='cdm_euclid_serial.dat',
                    charge_injection=44500.,
                    lines: t.Optional[dict] = None):
    # from CTI import CTI

    if lines is None:
        lines = dict(ystart1=1064,
                     ystop1=1075,
                     xstart1=577,
                     xstop1=588)

    trapdata = np.loadtxt(parallel)
    nt_p = trapdata[:, 0]
    sigma_p = trapdata[:, 1]
    taur_p = trapdata[:, 2]

    trapdata = np.loadtxt(serial)
    nt_s = trapdata[:, 0]
    sigma_s = trapdata[:, 1]
    taur_s = trapdata[:, 2]

    # create a quadrant
    CCD = np.zeros((2066, 2048), dtype=np.float32)

    # add horizontal charge injection lines
    CCD[lines['ystart1']:lines['ystop1'], :] = charge_injection
    write_fits_file(CCD.copy(), 'ChargeHtest.fits', unsigned16bit=False)

    # radiate CTI to plot initial set trails
    c = CDM03Python({}, [])
    CCDCTIhor = c.apply_radiation_damage(CCD.copy(), nt_p, sigma_p, taur_p, nt_s, sigma_s, taur_s)    # , rdose=1.6e10)
    write_fits_file(CCDCTIhor, 'CTIHtest.fits', unsigned16bit=False)

    # parallel = np.average(CCDCTIhor, axis=1)

    # now serial
    CCD = np.zeros((2066, 2048), dtype=np.float32)

    # add horizontal charge injection lines
    CCD[:, lines['xstart1']:lines['xstop1']] = charge_injection
    write_fits_file(CCD, 'ChargeVtest.fits', unsigned16bit=False)

    # radiate CTI to plot initial set trails
    c = CDM03Python({}, [])
    CCDCTI = c.apply_radiation_damage(CCD.copy(), nt_p, sigma_p, taur_p, nt_s, sigma_s, taur_s)   # , rdose=1.6e10)
    write_fits_file(CCDCTI, 'CTIVtest.fits', unsigned16bit=False)

    # plot trails
    # serial = np.average(CCDCTI, axis=0)

    # get parallel measurements
    # indp, parallelValues = parallelMeasurements(return_scale=True)
    # inds, serialValues = serialMeasurements(return_scale=True)

    # mask out irrelevant values
    # mskp = indp > -5
    # msks = inds > -5
    # indp = indp[mskp][:100]
    # inds = inds[msks][:250]
    # parallelValues = parallelValues[mskp][:100]
    # serialValues = serialValues[msks][:250]

    # rescale
    # indp += 185
    # inds += 10

    # cutout right region
    # shift = 5
    # profileParallelM = parallel[lines['ystop1'] - shift:lines['ystop1'] - shift + len(indp)]
    # profileSerialM = serial[lines['xstop1'] - shift: lines['xstop1'] - shift + len(inds)]

    # set up the charge injection charge_injection positions
    # fig = plt.figure()
    # fig.suptitle('CCD204 05325-03-02 Hopkinson EPER at 200kHz, with 20.48ms, 8e9 at 10MeV')
    # fig.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
    # ax1 = fig.add_subplot(211)
    # ax2 = fig.add_subplot(212)
    # 
    # ax1.set_title('Parallel CTI')
    # ax2.set_title('Serial CTI')

    # ax1.semilogy(indp, parallelValues, 'bo', ms=3, label='152.55K')
    # ax1.semilogy(indp, profileParallelM, 'y-', label='MSSL')

    # ax2.semilogy(inds, serialValues, 'bs', ms=3, label='152.5K')
    # ax2.semilogy(inds, profileSerialM, 'y-', label='MSSL')

    # ax1.set_ylim(1., 60000)
    # ax2.set_ylim(1., 60000)
    # 
    # ax1.set_xlim(180, 250)
    # ax2.set_xlim(0, 220)

    # ax2.set_xlabel('Pixels')
    # ax1.set_ylabel('Photoelectrons')
    # ax2.set_ylabel('Photoelectrons')
    # ax1.legend(fancybox=True, shadow=True, numpoints=1)
    # ax2.legend(fancybox=True, shadow=True, numpoints=1)
    # plt.savefig('PythonCDM03.pdf')
    # plt.close()


def parallelMeasurements(filename='CCD204_05325-03-02_Hopkinson_EPER_data_200kHz_one-output-mode_1.6e10-50MeV.txt',
                         datafolder='/Users/sammy/EUCLID/CTItesting/data/', 
                         gain1=1.17, 
                         limit=105, 
                         return_scale=False):
    """

    :param filename:
    :param datafolder:
    :param gain1:
    :param limit:
    :param return_scale:
    :return:
    """
    tmp = np.loadtxt(datafolder + filename, usecols=(0, 5)) #5 = 152.55K
    ind = tmp[:, 0]
    values = tmp[:, 1]
    values *= gain1
    if return_scale:
        return ind, values
    else:
        values = values[ind > -5.]
        values = np.abs(values[:limit])
        return values


def serialMeasurements(filename='CCD204_05325-03-02_Hopkinson-serial-EPER-data_200kHz_one-output-mode_1.6e10-50MeV.txt',
                       datafolder='/Users/sammy/EUCLID/CTItesting/data/',
                       gain1=1.17,
                       limit=105,
                       return_scale=False):
    """

    :param filename:
    :param datafolder:
    :param gain1:
    :param limit:
    :param return_scale:
    :return:
    """
    tmp = np.loadtxt(datafolder + filename, usecols=(0, 6)) #6 = 152.55K
    ind = tmp[:, 0]
    values = tmp[:, 1]
    values *= gain1
    if return_scale:
        return ind, values
    else:
        values = values[ind > -5.]
        values = np.abs(values[:limit])
        return values


def write_fits_file(data, output, unsigned16bit=True):
    """
    Write out FITS files using PyFITS.

    :param data: data to write to a FITS file
    :type data: ndarray
    :param output: name of the output file
    :type output: string
    :param unsigned16bit: whether to scale the data using bzero=32768
    :type unsigned16bit: bool

    :return: None
    """
    if os.path.isfile(output):
        os.remove(output)

    #create a new FITS file, using HDUList instance
    ofd = pf.HDUList(pf.PrimaryHDU())

    #new image HDU
    hdu = pf.ImageHDU(data=data)

    #convert to unsigned 16bit int if requested
    if unsigned16bit:
        hdu.scale('int16', '', bzero=32768)
        hdu.header.add_history('Scaled to unsigned 16bit integer!')

    #update and verify the header
    hdu.header.add_history('If questions, please contact Sami-Matias Niemi (s.niemi at ucl.ac.uk).')
    hdu.header.add_history('This file has been created with the VISsim Python Package at %s' \
                           % datetime.datetime.isoformat(datetime.datetime.now()))
    hdu.verify('fix')

    ofd.append(hdu)

    #write the actual file
    ofd.writeto(output)


def ThibautsCDM03params():
    return dict(beta_p=0.29, beta_s=0.12,
                fwc=200000.,
                vth=162222.38231975277,    # vth in wrong units now?
                t=2.1e-2,
                vg=7.2e-11,
                st=5.0e-6,
                sfwc=1450000.,
                svg=3.00E-10)


def MSSLCDM03params():
    return dict(beta_p=0.29, beta_s=0.29,
                fwc=200000.,
                vth=1.168e7,
                t=20.48e-3,
                vg=6.e-11,
                st=5.e-6,
                sfwc=730000.,
                svg=1.2e-10)