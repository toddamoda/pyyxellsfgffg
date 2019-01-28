"""Unit tests for class `Detector`."""

import pytest
from copy import deepcopy
# from pyxel.detectors.ccd import CCD
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.ccd_geometry import CCDGeometry
from pyxel.detectors.characteristics import Characteristics
# from pyxel.detectors.cmos import CMOS
from pyxel.detectors.cmos_characteristics import CMOSCharacteristics
from pyxel.detectors.cmos_geometry import CMOSGeometry
from pyxel.detectors.detector import Detector
from pyxel.detectors.environment import Environment
from pyxel.detectors.geometry import Geometry
from pyxel.detectors.material import Material
# from pyxel.data_structure.photon import Photon


@pytest.mark.parametrize("geometry, environment, characteristics, material", [
    (Geometry(), Environment(), Characteristics(), Material()),
    (Geometry(), Environment(), CCDCharacteristics(), Material()),
    (Geometry(), Environment(), CMOSCharacteristics(), Material()),

    (CCDGeometry(), Environment(), Characteristics(), Material()),
    (CCDGeometry(), Environment(), CCDCharacteristics(), Material()),
    (CCDGeometry(), Environment(), CMOSCharacteristics(), Material()),

    (CMOSGeometry(), Environment(), Characteristics(), Material()),
    (CMOSGeometry(), Environment(), CCDCharacteristics(), Material()),
    (CMOSGeometry(), Environment(), CMOSCharacteristics(), Material())
])
def test_init(geometry, environment, characteristics, material):
    """Test Detector.__init__ with valid entries."""

    # Create a `Detector`
    obj = Detector(geometry=geometry,
                   environment=environment,
                   characteristics=characteristics,
                   material=material)

    # Test getters
    assert obj.geometry is geometry
    assert obj.environment is environment
    assert obj.characteristics is characteristics
    assert obj.material is material

    assert obj.photons is not None
    assert obj.charges is not None
    assert obj.pixels is not None
    assert obj.signal is not None
    assert obj.image is not None


@pytest.mark.parametrize("obj, other_obj", [
    (Detector(Geometry(), Material(), Environment(), Characteristics()),        # TODO
     Detector(Geometry(), Material(), Environment(), Characteristics())),
    (Detector(CCDGeometry(), Material(), Environment(), Characteristics()),
     Detector(CCDGeometry(), Material(), Environment(), Characteristics())),
    (Detector(CMOSGeometry(), Material(), Environment(), Characteristics()),
     Detector(CMOSGeometry(), Material(), Environment(), Characteristics())),

    (Detector(Geometry(), Material(), Environment(), CCDCharacteristics()),
     Detector(Geometry(), Material(), Environment(), CCDCharacteristics())),        # TODO
    (Detector(CCDGeometry(), Material(), Environment(), CCDCharacteristics()),
     Detector(CCDGeometry(), Material(), Environment(), CCDCharacteristics())),
    (Detector(CMOSGeometry(), Material(), Environment(), CCDCharacteristics()),
     Detector(CMOSGeometry(), Material(), Environment(), CCDCharacteristics())),

    (Detector(Geometry(), Material(), Environment(), CMOSCharacteristics()),               # TODO
     Detector(Geometry(), Material(), Environment(), CMOSCharacteristics())),
    (Detector(CCDGeometry(), Material(), Environment(), CMOSCharacteristics()),
     Detector(CCDGeometry(), Material(), Environment(), CMOSCharacteristics())),
    (Detector(CMOSGeometry(), Material(), Environment(), CMOSCharacteristics()),
     Detector(CMOSGeometry(), Material(), Environment(), CMOSCharacteristics())),
])
def test_eq(obj, other_obj):
    """Test Detector.__eq__."""
    assert type(obj) is Detector


@pytest.mark.parametrize("obj", [
    Detector(Geometry(), Material(), Environment(), Characteristics()),
])
def test_copy(obj):
    """Test Detector.copy."""
    assert type(obj) is Detector
    id_obj = id(obj)
    new_obj = deepcopy(obj)
    assert id_obj == id(obj)
    assert new_obj is not obj
