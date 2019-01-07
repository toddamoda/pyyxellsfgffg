"""Test `PyxelLoader` with `Environment`."""
import pytest
from pyxel.detectors.environment import Environment
import esapy_config as om


@pytest.mark.skip(reason=None)
def test_loader():
    """Test `PyxelLoader`."""
    data = """
!environment
  temperature: 3.14
  total_ionising_dose: 1.0
  total_non_ionising_dose: 1.0
"""

    obj = om.load(data)

    assert isinstance(obj, Environment)
    assert obj.temperature == 3.14


@pytest.mark.skip(reason=None)
def test_dumper():
    """Test `PyxelDumper`."""
    obj = Environment(temperature=100.234,
                      total_ionising_dose=1.0,
                      total_non_ionising_dose=1.0)

    data = om.dump(obj)
    # data = dump(obj)
    pass

    assert data == """!environment
temperature: 100.234
total_ionising_dose: 1.0
total_non_ionising_dose: 1.0
"""
