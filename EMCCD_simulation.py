import os
import pyxel
import numpy as np
from astropy.io import fits


"""
This script will take .fits files from a specified folder,
and run then through a user defined exposure model of PyXel.

Settings, and output folder path must be specified in the .yaml file.
Input file path/location must be specified in this script.
Define lowflux_path to pyescelle files
Define path to exposure5.yaml in config = pyxel.load('')   
User can define naming convention in last line
"""

#define path to files
lowflux_path= 'C:/Users/akade/Documents/Physics/Data Processing/thesis/RawData/em_sky_low_flux'

#initialize array to contain file names
lf_files = []

#find files with .fits endings in path
for file in os.listdir(lowflux_path):
    if file.endswith('.fits'):
        lf_files.append(os.path.join(file))
        
        
#write in the image_file from the array and loop over all files
for k in np.arange(len(lf_files)):
    config=pyxel.load('C:/Users/akade/Documents/Physics/PyXel-EMCCD/exposure6.yaml')
    config.pipeline.photon_collection.load_image._arguments.image_file = (lowflux_path + '/' + lf_files[k])

    exposure = config.exposure  # class Exposure
    detector = config.ccd_detector  # class CCD
    pipeline = config.pipeline  # class DetectionPipeline



    result = pyxel.exposure_mode(
        exposure=exposure,
        detector=detector,
        pipeline=pipeline,
    )

    result
    
#%%
"""
If you would like the .fits files to be ordered and numbered outside the pyxel run folders run this script
"""    
# Takes the directory output path to be the same as the one specified in the .yaml
directory_path = str(config.exposure.outputs.output_dir.parent)

# Get a list of all subdirectories in the directory_path
subdirectories = [os.path.join(directory_path, name) for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))]

# Loop over each subdirectory, and find all files ending with '.fits'
fits_files = []
for subdirectory in subdirectories:
    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if file.endswith('.fits'):
                fits_files.append(os.path.join(root, file))


for i in np.arange(len(fits_files)):
    hdu = fits.PrimaryHDU(fits.getdata(fits_files[i])*1.0)
    hdu1 = fits.HDUList([hdu])
    hdu1.writeto(directory_path + '/low_flux_' +str(i+1) + '.fits')
    
