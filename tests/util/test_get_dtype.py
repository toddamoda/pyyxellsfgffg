import numpy as np
import pytest

from pyxel.util import get_dtype


@pytest.mark.parametrize(
    "bit_resolution, exp_dtype",
    [
        (1, np.dtype(np.uint8)),
        (8, np.dtype(np.uint8)),
        (9, np.dtype(np.uint16)),
        (16, np.dtype(np.uint16)),
        (17, np.dtype(np.uint32)),
        (32, np.dtype(np.uint32)),
        (33, np.dtype(np.uint64)),
        (64, np.dtype(np.uint64)),
    ],
)
def test_get_dtype(bit_resolution, exp_dtype):
    """Test function 'get_dtype'."""
    result = get_dtype(bit_resolution)
    assert result == exp_dtype
