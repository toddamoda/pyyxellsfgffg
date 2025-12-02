#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

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
