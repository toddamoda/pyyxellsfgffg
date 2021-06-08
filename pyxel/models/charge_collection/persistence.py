#   --------------------------------------------------------------------------
#   Copyright 2019 SCI-FIV, ESA (European Space Agency)
#   Written by B. Serra
#   --------------------------------------------------------------------------
"""Pyxel persistence model."""
import logging

import numpy as np
from astropy.io import fits

from pyxel.detectors import CMOS


# @validators.validate
# @config.argument(name='', label='', units='', validate=)
def simple_persistence(
    detector: CMOS, trap_timeconstants: list, trap_densities: list
) -> None:
    """Trapping/detrapping charges."""
    logging.info("Persistence")
    if "persistence" not in detector._memory.keys():
        detector._memory["persistence"] = dict()
        for trap_density, trap_timeconstant in zip(trap_densities, trap_timeconstants):
            entry = "".join(
                ["trappedCharges_", str(trap_density), "-", str(trap_timeconstant)]
            )
            detector._memory["persistence"].update(
                {entry: np.zeros((detector.geometry.row, detector.geometry.col))}
            )
    else:
        for trap_density, trap_timeconstant in zip(trap_densities, trap_timeconstants):
            entry = "".join(
                ["trappedCharges_", str(trap_density), "-", str(trap_timeconstant)]
            )
            trapped_charges = detector._memory["persistence"][entry]
            # Trap density is a scalar for now, in the future we could feed maps?
            # the delta t is fixed to 0.5 s, need to find a way to avoid problem of divergence
            trapped_charges = trapped_charges + (0.5 / trap_timeconstant) * (
                detector.pixel.array * trap_density - trapped_charges
            )
            # Remove the trapped charges from the pixel
            detector.pixel.array -= trapped_charges.astype(np.int32)
            # Replace old trapped charges map in the detector's memory
            detector._memory["persistence"][entry] = trapped_charges
            
    return None

def current_persistence(
    detector: CMOS, trap_timeconstants: list, trap_densities: str, trap_max: str, trap_proportions: list) -> None:
    """Trapping/detrapping charges."""
    logging.info("Persistence")
    # If the file for trap density is correct open it and use it
    # otherwise I need to define a default trap density map
    
    # Extract trap density / full well
    trap_densities = fits.open(trap_densities)[0].data[0:450, 0:450]
    trap_densities[np.where(trap_densities<0)] = 0
    # Print the median of the max amount of traps
    #print (np.nanmedian(trap_densities))
    
    # Extract the max amount of trap by long soak
    trap_max = fits.open(trap_max)[0].data[0:450, 0:450]
    trap_max[np.where(trap_max<0)] = 0
    
    # Print the median of the max amount of traps
    #print (np.nanmedian(trap_max))
    #print (np.nanmedian(detector.pixel.array))
    
    # If there is no entry for persistence in the memory of the detector
    # create one
    if "persistence" not in detector._memory.keys():
        detector._memory["persistence"] = dict()
        for trap_proportion, trap_timeconstant in zip(trap_proportions, trap_timeconstants):
            entry = "".join(
                ["trappedCharges_", str(trap_proportion), "-", str(trap_timeconstant)]
            )
            detector._memory["persistence"].update(
                {entry: np.zeros((detector.geometry.row, detector.geometry.col))}
            )
            trapped_charges = detector._memory["persistence"][entry]
    
    # For each trap population
    for trap_proportion, trap_timeconstant in zip(trap_proportions, trap_timeconstants):
        
        # Get the correct persistence traps entry
        entry = "".join(
            ["trappedCharges_", str(trap_proportion), "-", str(trap_timeconstant)]
        )
        
        # Select the trapped charges array
        trapped_charges = detector._memory["persistence"][entry]
        
        # Time for reading a frame
        #delta_t = (detector.geometry.row * detector.geometry.col)/detector.characteristics.readout_freq
        delta_t = 1.41
        
        # Computer trapped charge for this increament of time
        # Time factor is the integration time divided by the time constant (1, 10, 100, 1000, 10000)
        time_factor = delta_t/trap_timeconstant
        
        # Amount of charges trapped per unit of full well
        max_charges = trap_densities * trap_proportion
        
        # Maximum of amount of charges trapped
        fw_trap = trap_max * trap_proportion
        
        diff = time_factor * (max_charges * detector.pixel.array * np.exp(-time_factor) - trapped_charges)
        # Compute trapped charges
        trapped_charges = trapped_charges + \
                          time_factor * (max_charges * detector.pixel.array * np.exp(-time_factor) - trapped_charges)
        #print ('-----')
        #print ('Time constant', trap_timeconstant)
        #print ('Trapped charges', trapped_charges)
        # When the amount of trapped charges is superior to the maximum of available traps, set to max 
        trapped_charges[np.where(trapped_charges>fw_trap)] = max_charges[np.where(trapped_charges>fw_trap)]
        # Can't have a negative amount of charges trapped
        trapped_charges[np.where(trapped_charges<0)] = 0 
        
        # Remove the trapped charges from the pixel
        #detector.pixel.array -= trapped_charges.astype(np.int32)
        detector.pixel.array -= diff.astype(np.int32)
        
        # Replace old trapped charges map in the detector's memory
        detector._memory["persistence"][entry] = trapped_charges

    return None
