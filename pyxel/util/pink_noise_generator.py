# Copyright or © or Copr. Antoine Kaszczyc and Aurelien Jarno, Centre de Recherche Astrophysique de Lyon (CRAL)  (2025)
#
# Antoine Kaszczyc <antoine.kaszczyc@univ-lyon1.fr>
# Aurelien Jarno <aurelien.jarno@univ-lyon1.fr>
#
# This file is part of the Pyxel general simulator framework.
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


""":term:`PinkNoiseGenerator` pink noise generator class."""

import numpy as np
from scipy.signal import freqz, lfilter, lfilter_zi


class PinkNoiseGenerator:
    """
    A class for generating pink noise using a filter-based method.

    This class implements a pink noise generator based on the method described
    by Julius O. Smith III for non-periodic pink noise generation. It generates
    pink noise by applying an Infinite Impulse Response (IIR) filter to white
    noise. The IIR filter used has a 1/f spectral roll-off, which is
    characteristic of pink noise.

    The generated pink noise is normalized to have a unit variance. The filter
    state is maintained between calls to ensure continuous generation of pink
    noise without discontinuities.

    An internal random number generator is initialized with a given seed,
    ensuring reproducibility of the noise sequence even if other calls to
    ``np.random`` are made between calls to the ``get`` method.

    Reference: https://ccrma.stanford.edu/~jos/sasp/Example_Synthesis_1_F_Noise.html
    """

    def __init__(self, seed=None):
        """
        Initialize the PinkNoiseGenerator instance.

        Sets up the filter coefficients, computes the normalization factor for
        unit variance, and initializes a random number generator and the
        internal filter state.

        Parameters
        ----------
        seed : {None, int, array_like[ints], SeedSequence, BitGenerator, Generator}, optional
            A seed to initialize the random number generator. It is passed
            directly to the ``np.random.default_rng`` method.
        """
        # Initialize the random number generator
        self.rng = np.random.default_rng(seed)

        # Filter coefficients for the IIR filter
        self.B = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        self.A = [1, -2.494956002, 2.017265875, -0.522189400]

        # Compute the filter response of the filter to estimate the gain
        _, h = freqz(self.B, self.A, worN=1000000)

        # Compute the Power Spectral Density gain from the filter response
        gain = np.square(np.abs(h))

        # Compute the variance, as the average over frequency
        var = gain.mean()
        self.sigma = np.sqrt(var)

        # Estimate the time to decay by 60 dB
        nt60 = round(np.log(1000) / (1 - max(abs(np.roots(self.A)))))

        # Initialize the filter with white noise
        noise = self.rng.standard_normal(nt60)
        self.zi = lfilter_zi(self.B, self.A) * noise[0]
        _, _zi = lfilter(self.B, self.A, noise, zi=self.zi)

    def get(self, size=1):
        """
        Generate samples of pink noise of the given size.

        This method generates samples of pink noise by filtering samples of a
        white noise through an IIR filter that implements a 1/f spectral
        roll-off. The resulting pink noise is then normalized to have unit
        variance.

        The filter state is maintained between calls to maintain continuity
        between noise samples.

        Parameters
        ----------
        size : int or None, optional
            The number of samples of pink noise to generate. Default is 1,
            which means a single value is returned

        Returns
        -------
        out: ndarray
            A floating-point array of shape ̀``size`` of pink noise or a single
            single sample if ``size`` was not specified.
        """

        # Generate a white noise
        noise = self.rng.standard_normal(size)

        # Filter the white noise to generate pink noise
        noise, self.zi = lfilter(self.B, self.A, noise, zi=self.zi)

        # Normalize the resulting noise
        noise /= self.sigma

        return noise
