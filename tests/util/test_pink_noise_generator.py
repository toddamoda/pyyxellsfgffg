# Copyright or © or Copr. Thibault Pichon, CEA Paris-Saclay (2023)
#
# Antoine Kaszczyc <antoine.kaszczyc@univ-lyon1.fr>
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

import numpy as np

from pyxel.util import PinkNoiseGenerator


def test_pink_noise_generator():
    assert isinstance(PinkNoiseGenerator(), PinkNoiseGenerator)
    assert isinstance(PinkNoiseGenerator(None), PinkNoiseGenerator)
    assert isinstance(PinkNoiseGenerator(1234), PinkNoiseGenerator)
    gen = PinkNoiseGenerator(1234)
    assert gen.get(1).shape == (1,)
    assert gen.get(10).shape == (10,)
    assert isinstance(gen.get(10)[0], float)
    assert isinstance(gen.get(10)[1], float)
    s = gen.get(1_000_000)
    assert abs(np.std(s) - 1) < 0.1
    assert abs(np.mean(s)) < 0.1
