"""
arCTIc (AlgoRithm for Charge Transfer Inefficiency Correction) is a program that can create or remove image trails
due to CTI, which is simulated via the modelling of trapping, releasing and the movement of charge along the pixels
inside a CCD.

Developed by James Nightingale, Richard Massey and Jacob Kegerris (University of Durham)
More information:
https://pypi.org/project/arcticpy/
"""


from arcticpy import main as ac
from arcticpy import ccd as accd
from arcticpy.roe import ROE
from arcticpy import traps as trp
import arcticpy as ac
from pyxel.detectors import CCD
import numpy as np
import typing as t


# CCD, ROE, and trap species parameters


def arctic(detector: CCD,
           well_fill_power: float,
           density: float,
           release_timescale: t.Sequence[float]) -> np.array:
    char = detector.characteristics
    image = detector.pixel.array
    image = image.astype(float)
    # image = ac.acs.FrameACS.from_fits(file_path=detector.pixel.array, quadrant_letter=quadrant_letter)
    ccd = accd.CCD(well_fill_power=well_fill_power, full_well_depth=char.fwc)
    roe = ROE()
    #ccd = ac.CCD(well_fill_power=well_fill_power, full_well_depth=char.fwc)
    #roe = ac.ROE()
    trap = trp.Trap(density=-density, release_timescale=release_timescale)
    image_cti_added = ac.add_cti(
        image=image,
        parallel_traps=[trap],
        parallel_ccd=ccd,
        parallel_roe=roe,
    )
    return image_cti_added

#Try to work out the imports better for the afternoon - struggling to get this stupid thing to imprt the things I want it to!!!!!!!!