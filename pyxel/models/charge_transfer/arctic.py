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


def arctic(detector: CCD,
           well_fill_power: float,
           density: float,
           release_timescale: t.Sequence[float]) -> np.ndarray:
    char = detector.characteristics
    image = detector.pixel.array
    image = image.astype(float)
    ccd = ac.CCD(well_fill_power=well_fill_power, full_well_depth=char.fwc)
    roe = ac.ROE()
    trap = ac.Trap(density=density, release_timescale=release_timescale)
    s = ac.add_cti(
        image=image,
        parallel_traps=[trap],
        parallel_ccd=ccd,
        parallel_roe=roe,
    )
    return s

