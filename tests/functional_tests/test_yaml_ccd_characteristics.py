"""Test `PyxelLoader` with `CCDChararacteristics`."""

import pytest
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.pipelines.yaml_processor import load
from pyxel.pipelines.yaml_processor import dump


@pytest.fixture
def content1():
    """Example of YAML content."""
    return """
    !ccd_characteristics
        k: 1
        j: 2
        qe: 3
        eta: 4
        sv: 5
        accd: 6
        a1: 7
        a2: 8    
    """


def test_loader(content1):
    """Test `PyxelLoader`."""
    obj = load(content1)

    assert isinstance(obj, CCDCharacteristics)
    assert obj.k == 1
    assert obj.j == 2
    assert obj.qe == 3
    assert obj.eta == 4
    assert obj.sv == 5
    assert obj.accd == 6
    assert obj.a1 == 7
    assert obj.a2 == 8


def test_dumper():
    """Test `PyxelDumper`."""
    obj = CCDCharacteristics(k=1, j=2, qe=3, eta=4, sv=5, accd=6, a1=7, a2=8)

    data = dump(obj)

    assert data == "!ccd_characteristics {a1: 7, a2: 8, accd: 6, eta: 4, j: 2, k: 1, qe: 3, sv: 5}\n"
