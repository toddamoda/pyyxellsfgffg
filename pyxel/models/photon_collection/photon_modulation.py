# --- File: pyxel/models/photon_collection/photon_modulation.py ---

import matplotlib.pyplot as plt
import numpy as np

from pyxel.detectors import Detector


def photon_flux_modulation(
    detector: Detector,
    modulation_type: str = "sin",
    amplitude: float = 0.2,
    frequency: float = 1.0,
    debug: bool = False,
) -> None:
    """Apply temporal modulation to photon flux and visualize modulation."""

    # --- Determine time array ---
    if hasattr(detector, "readout_times") and detector.readout_times is not None:
        time = np.asarray(detector.readout_times)
    elif hasattr(detector, "exposure") and hasattr(detector.exposure, "readout"):
        time = np.asarray(detector.exposure.readout.times)
    else:
        # fallback: simulate a synthetic time series if Pyxel didn't pass one
        time = np.linspace(0, 1, 100)

    print(f"[photon_flux_modulation] Readout time samples: {time}")
    print(f"Total time steps: {len(time)}")

    # --- Initialize a dummy photon flux cube ---
    # If detector doesn't yet have a photon array, create one
    if (
        not hasattr(detector, "photon")
        or getattr(detector.photon, "array", None) is None
    ):
        flux = np.ones((len(time), 10, 10))
    else:
        flux = detector.photon.array
        if flux.ndim == 2:
            flux = np.broadcast_to(flux, (len(time), *flux.shape)).copy()

    # --- Compute modulation factor ---
    if modulation_type == "sin":
        mod_factor = 1.0 + amplitude * np.sin(2 * np.pi * frequency * time)
    elif modulation_type == "square":
        mod_factor = 1.0 + amplitude * np.sign(np.sin(2 * np.pi * frequency * time))
    else:
        mod_factor = np.ones_like(time)

    # --- Apply modulation ---
    mod_factor = mod_factor[:, None, None]
    modulated_flux = flux * mod_factor

    # Average over time to maintain Pyxel’s expected 2D photon array
    detector.photon.array = modulated_flux.mean(axis=0)

    # --- Visualization (debug mode) ---
    if debug:
        plt.figure(figsize=(6, 3))
        plt.plot(
            time, mod_factor.squeeze(), label="Modulation Factor", color="deepskyblue"
        )
        plt.title("Photon Flux Modulation Over Time")
        plt.xlabel("Time [s]")
        plt.ylabel("Relative Flux")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()
