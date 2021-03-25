"""
arCTIc (AlgoRithm for Charge Transfer Inefficiency Correction) is a program that can create or remove image trails
due to CTI, which is simulated via the modelling of trapping, releasing and the movement of charge along the pixels
inside a CCD.

Developed by James Nightingale, Richard Massey and Jacob Kegerris (University of Durham)
More information:
https://pypi.org/project/arcticpy/
"""


import arcticpy as ac
from pyxel.detectors import CCD
import numpy as np
import typing as t

# CCD, ROE, and trap species parameters



def arctic(detector: CCD,
            quadrant_letter: str,
            well_fill_power: float,
            density: float,
            release_timescale: t.Sequence[float]) -> np.array:

    char = detector.characteristics
    image = ac.acs.FrameACS.from_fits(file_path=detector.pixel.array, quadrant_letter=quadrant_letter)
    ccd = ac.CCD(well_fill_power=well_fill_power, full_well_depth=char.fwc)
    roe = ac.ROE()
    trap = ac.Trap(density=-density, release_timescale=release_timescale)
    image_cti_added = ac.add_cti(
        image=image,
        parallel_traps=[trap],
        parallel_ccd=ccd,
        parallel_roe=roe,
    )
    return image_cti_added
