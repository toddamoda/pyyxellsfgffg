from pyxel.detectors.ccd import CCD
from pyxel.detectors.environment import Environment
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.geometry import Geometry
# from pyxel.pipelines.yaml_processor import dump
from pyxel.pipelines.yaml_processor import load


def test_loader_with_extra_tags():
    """Test `PyxelLoader`"""
    data = """
!CCD
  photons: 10
  image: null

  geometry: !geometry
   row: 1000
   col: 1001
   depletion_thickness: 1.0
   field_free_thickness: 2.0
   total_thickness: 3.0
   pixel_vert_size: 4.0
   pixel_horz_size: 5.0
   # material: foo
   n_acceptor: 6.0
   n_donor: 7.0
   bias_voltage: 8.0

  environment: !environment
    temperature: 3.14

  characteristics: !ccd_characteristics
    qe: 3
    eta: 4
    sv: 5
    accd: 6
    a1: 7
    a2: 8
"""

    obj = load(data)

    assert isinstance(obj, CCD)
    # assert obj.photons == 10
    # assert obj.image is None

    assert isinstance(obj.geometry, Geometry)
    assert obj.geometry.row == 1000
    assert obj.geometry.col == 1001
    assert obj.geometry.depletion_thickness == 1.0
    assert obj.geometry.field_free_thickness == 2.0
    assert obj.geometry.total_thickness == 3.0
    assert obj.geometry.pixel_vert_size == 4.0
    assert obj.geometry.pixel_horz_size == 5.0
    # assert obj.geometry.material == 'foo'
    assert obj.geometry.n_acceptor == 6.0
    assert obj.geometry.n_donor == 7.0
    assert obj.geometry.bias_voltage == 8.0

    assert isinstance(obj.environment, Environment)
    assert obj.environment.temperature == 3.14

    assert isinstance(obj.characteristics, CCDCharacteristics)
    # assert obj.characteristics.k == 1
    # assert obj.characteristics.j == 2
    assert obj.characteristics.qe == 3
    assert obj.characteristics.eta == 4
    assert obj.characteristics.sv == 5
    assert obj.characteristics.accd == 6
    assert obj.characteristics.a1 == 7
    assert obj.characteristics.a2 == 8


def test_loader2_without_extra_tags():
    """Test `PyxelLoader`"""
    data = """
!CCD
  photons: 10
  image: null

  geometry:
   row: 1000
   col: 1001
   depletion_thickness: 1.0
   field_free_thickness: 2.0
   total_thickness: 3.0
   pixel_vert_size: 4.0
   pixel_horz_size: 5.0
   # material: foo
   n_acceptor: 6.0
   n_donor: 7.0
   bias_voltage: 8.0

  environment:
    temperature: 3.14

  characteristics:
    qe: 3
    eta: 4
    sv: 5
    accd: 6
    a1: 7
    a2: 8
"""

    obj = load(data)

    assert isinstance(obj, CCD)
    # assert obj.photons == 10
    # assert obj.image is None

    assert isinstance(obj.geometry, Geometry)
    assert obj.geometry.row == 1000
    assert obj.geometry.col == 1001
    assert obj.geometry.depletion_thickness == 1.0
    assert obj.geometry.field_free_thickness == 2.0
    assert obj.geometry.total_thickness == 3.0
    assert obj.geometry.pixel_vert_size == 4.0
    assert obj.geometry.pixel_horz_size == 5.0
    # assert obj.geometry.material == 'foo'
    assert obj.geometry.n_acceptor == 6.0
    assert obj.geometry.n_donor == 7.0
    assert obj.geometry.bias_voltage == 8.0

    assert isinstance(obj.environment, Environment)
    assert obj.environment.temperature == 3.14

    assert isinstance(obj.characteristics, CCDCharacteristics)
    # assert obj.characteristics.k == 1
    # assert obj.characteristics.j == 2
    assert obj.characteristics.qe == 3
    assert obj.characteristics.eta == 4
    assert obj.characteristics.sv == 5
    assert obj.characteristics.accd == 6
    assert obj.characteristics.a1 == 7
    assert obj.characteristics.a2 == 8
