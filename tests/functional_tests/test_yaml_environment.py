"""Test `PyxelLoader` with `Environment`."""

from pyxel.detectors.environment import Environment
from pyxel.io.yaml_processor import dump
from pyxel.io.yaml_processor import load


def test_loader():
    """Test `PyxelLoader`."""
    data = """
!environment
  temperature: 3.14
  total_ionising_dose: 1.0
  total_non_ionising_dose: 1.0
"""

    obj = load(data)

    assert isinstance(obj, Environment)
    assert obj.temperature == 3.14


def test_dumper():
    """Test `PyxelDumper`."""
    obj = Environment(temperature=100.234,
                      total_ionising_dose=1.0,
                      total_non_ionising_dose=1.0)

    data = dump(obj)

    assert data == """!environment
temperature: 100.234
total_ionising_dose: 1.0
total_non_ionising_dose: 1.0
"""