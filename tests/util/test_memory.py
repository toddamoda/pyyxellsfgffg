#  Copyright (c) European Space Agency, 2017.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


import sys

import pytest

from pyxel.util import memory_usage_details


def test_no_attributes(ccd_empty):
    with pytest.raises(ValueError, match=r"No attributes provided"):
        memory_usage_details(ccd_empty)


def test_invalid_attribute(ccd_empty):
    with pytest.raises(AttributeError):
        memory_usage_details(ccd_empty, ["dummy"])


@pytest.mark.skip(reason="Fix this test !")
@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="Different value for older versions."
)
def test_memory_usage(ccd_empty):
    attributes = [
        "_photon",
        "_charge",
        "_pixel",
        "_signal",
        "_image",
        "environment",
        "_geometry",
        "_characteristics",
    ]

    usage = memory_usage_details(ccd_empty, attributes, print_result=False)

    empty_size = {
        "characteristics": 1160,
        "charge": 43896,
        "environment": 512,
        "geometry": 664,
        "image": 432,
        "pixel": 432,
        "signal": 432,
    }

    assert usage == empty_size
