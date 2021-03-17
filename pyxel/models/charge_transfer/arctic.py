"""
arCTIc (AlgoRithm for Charge Transfer Inefficiency Correction) is a program that can create or remove image trails
due to CTI, which is simulated via the modelling of trapping, releasing and the movement of charge along the pixels
inside a CCD.

Developed by James Nightingale, Richard Massey and Jacob Kegerris (University of Durham)
More information:
https://pypi.org/project/arcticpy/
"""


import arcticpy as ac



# CCD, ROE, and trap species parameters



def add_cti(file_path, quadrant_letter, well_fill_power, full_well_depth,density, release_timescale ):


    image = ac.acs.FrameACS.from_fits(file_path=file_path, quadrant_letter=quadrant_letter)
    ccd = ac.CCD(well_fill_power=well_fill_power, full_well_depth=full_well_depth)
    roe = ac.ROE()
    trap = ac.Trap(density=-density, release_timescale=release_timescale)
    image_cti_added = ac.add_cti(
        image=image,
        parallel_traps=[trap],
        parallel_ccd=ccd,
        parallel_roe=roe,
    )
    return image_cti_added
