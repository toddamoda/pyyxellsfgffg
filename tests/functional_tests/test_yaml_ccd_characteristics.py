"""Test `PyxelLoader` with `CCDChararacteristics`."""

from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.io.yaml_processor import dump
from pyxel.io.yaml_processor import load


def test_loader():
    """Test `PyxelLoader`."""
    data = """
!ccd_characteristics
  qe: 3
  eta: 4
  sv: 5
  accd: 6
  a1: 7
  a2: 8
  fwc_parallel: 2
  fwc_serial: 3
"""

    obj = load(data)

    assert isinstance(obj, CCDCharacteristics)
    assert obj.qe == 3
    assert obj.eta == 4
    assert obj.sv == 5
    assert obj.accd == 6
    assert obj.a1 == 7
    assert obj.a2 == 8
    assert obj.fwc_parallel == 2
    assert obj.fwc_serial == 3


def test_dumper():
    """Test `PyxelDumper`."""
    obj = CCDCharacteristics(qe=3, eta=4, sv=5, accd=6, a1=7, a2=8, fwc_parallel=2, fwc_serial=3)

    data = dump(obj)

    assert data == "!ccd_characteristics {qe: 3, eta: 4, sv: 5, accd: 6, a1: 7, a2: 8, fwc_parallel: 2, fwc_serial: 3}\n"
