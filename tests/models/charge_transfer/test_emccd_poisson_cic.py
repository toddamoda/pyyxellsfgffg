import pytest

from pyxel.detectors import CCD
from pyxel.models.charge_transfer.EMCCD_poisson_cic import multiplication_register


def test_multiplication_register(ccd_10x10: CCD):
    detector = ccd_10x10

    multiplication_register(detector=detector, total_gain=0.0, gain_elements=1, pcic_rate=0.0, scic_rate=0.0)


@pytest.mark.parametrize(
    "total_gain,gain_elements,pcic_rate,scic_rate",
    [
        (-1, 10, 0.0, 0.0),
        (1, -1, -1, 1),
        (-1, -1, .005, -0.02),
    ],
)
def test_multiplication_register_bad_inputs(ccd_10x10: CCD, total_gain, gain_elements, pcic_rate, scic_rate):
    detector = ccd_10x10

    with pytest.raises(ValueError, match="Wrong input parameter"):
        multiplication_register(
            detector=detector, total_gain=total_gain, gain_elements=gain_elements, pcic_rate=pcic_rate, scic_rate=scic_rate
        )
