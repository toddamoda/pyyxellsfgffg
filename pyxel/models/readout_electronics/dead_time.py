#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Dead-time filtering model."""

import astropy.constants as const
import astropy.units as u
import numpy as np

from pyxel.detectors import MKID


def apply_dead_time_filter(phase_2d: np.ndarray, maximum_count: float) -> np.ndarray:
    """Apply the dead-time filter.

    Parameters
    ----------
    phase_2d : ndarray
    maximum_count : float

    Returns
    -------
    ndarray
    """
    return np.clip(phase_2d, a_min=None, a_max=maximum_count)


def dead_time_filter(
    detector: MKID,
    tau_0: float = 4.4 * 1.0e-7,
    n_0: float = 1.72 * 1.0e10,
    t_c: float = 1.26,
    v: float = 30.0,
    t_op: float = 0.3,
    tau_pb: float = 2.8 * 1.0e-10,
    tau_esc: float = 1.4 * 1.0e-10,
    tau_sat: float = 1.0e-3,
) -> None:
    """Apply a dead-time filter to the MKID detector phase array.

    Supports both static (2D) and time-dependent (3D) phase data if `readout_times`
    are available in the detector.
    """
    # Validation
    if not isinstance(detector, MKID):
        raise TypeError("Expecting an `MKID` object for 'detector'.")

    # Boltzmann's constant [eV K^-1]
    boltzmann_cst: float = const.k_B.to(u.eV / u.K).value

    # Compute superconducting gap energy
    delta: float = 1.76 * boltzmann_cst * t_c

    # Compute number of quasiparticles in the superconducting volume V
    n_qp: float = (
        2.0
        * v
        * n_0
        * np.sqrt(2.0 * np.pi * boltzmann_cst * t_op * delta)
        * np.exp(-delta / (boltzmann_cst * t_op))
    )

    # Compute recombination constant
    recombination_cst: float = (2.0 * delta**2) / (
        tau_0 * n_0 * (boltzmann_cst * t_c) ** 3
    )

    # Compute intrinsic quasiparticle lifetime
    tau_qp: float = v / (recombination_cst * n_qp)

    # Compute apparent quasi-particle lifetime (including saturation)
    tau_apparent_sat: float = 1.0 / (
        2.0 / (tau_qp * (1.0 + (tau_esc / tau_pb))) + (1.0 / tau_sat)
    )

    dead_time = tau_apparent_sat
    max_count = 1.0 / dead_time

    # --- NEW: handle time-dependent MKID data ---
    if hasattr(detector, "readout_times") and detector.readout_times is not None:
        readout_times = np.asarray(detector.readout_times)
        n_t = len(readout_times)
        phase_data = detector.phase.array

        # Expect shape (n_t, y, x) or (y, x)
        if phase_data.ndim == 2:
            # No time dimension → fallback to legacy 2D
            filtered_phase = apply_dead_time_filter(phase_data, maximum_count=max_count)
            detector.phase.array = filtered_phase

        elif phase_data.ndim == 3 and phase_data.shape[0] == n_t:
            # Apply dead-time filter for each time slice
            filtered = np.empty_like(phase_data)
            for i in range(n_t):
                filtered[i, :, :] = apply_dead_time_filter(
                    phase_data[i, :, :], maximum_count=max_count
                )
            detector.phase.array = filtered

        else:
            raise ValueError(
                f"Unexpected phase array shape {phase_data.shape}. "
                f"Expected (y, x) or ({n_t}, y, x) to match readout_times."
            )

    else:
        # Legacy path — single static phase image
        phase_2d = detector.phase.array
        detector.phase.array = apply_dead_time_filter(
            phase_2d=phase_2d,
            maximum_count=max_count,
        )
