import pytest
from pyxel.detectors.ccd import CCD
from pyxel.detectors.ccd_characteristics import CCDCharacteristics
from pyxel.detectors.ccd_geometry import CCDGeometry
from pyxel.detectors.material import Material
from pyxel.detectors.environment import Environment
import esapy_config.io as io


@pytest.mark.skip(reason=None)
def test_loader_with_extra_tags():
    """Test `PyxelLoader`."""
    # bias_voltage: 8.0
    data = """
!CCD
  geometry: !ccd_geometry
   row: 1000
   col: 1001
   total_thickness: 3.0
   pixel_vert_size: 4.0
   pixel_horz_size: 5.0
   # material: foo
   n_acceptor: 6.0
   n_donor: 7.0

  environment: !environment
    temperature: 3.14

  characteristics: !ccd_characteristics
    qe: 3
    eta: 4
    sv: 5
    amp: 6
    a1: 7
    a2: 8
"""

    obj = io.load(data)

    assert isinstance(obj, CCD)
    # assert obj.photons == 10
    # assert obj.image is None

    assert isinstance(obj.geometry, CCDGeometry)
    assert obj.geometry.row == 1000
    assert obj.geometry.col == 1001
    assert obj.geometry.total_thickness == 3.0
    assert obj.geometry.pixel_vert_size == 4.0
    assert obj.geometry.pixel_horz_size == 5.0
    # assert obj.geometry.material == 'foo'
    # assert obj.geometry.bias_voltage == 8.0

    assert isinstance(obj.material, Material)
    assert obj.material.n_acceptor == 6.0
    assert obj.material.n_donor == 7.0

    assert isinstance(obj.environment, Environment)
    assert obj.environment.temperature == 3.14

    assert isinstance(obj.characteristics, CCDCharacteristics)
    assert obj.characteristics.qe == 3
    assert obj.characteristics.eta == 4
    assert obj.characteristics.sv == 5
    assert obj.characteristics.amp == 6
    assert obj.characteristics.a1 == 7
    assert obj.characteristics.a2 == 8


@pytest.mark.skip(reason=None)
def test_dumper():
    """Test `PyxelLoader`."""
    obj = CCD(geometry=CCDGeometry(row=1000, col=1001,
                                   total_thickness=3.0, pixel_vert_size=4.0,
                                   pixel_horz_size=5.0),    # bias_voltage=8.0),
              material=Material(n_acceptor=6.0,
                                n_donor=7.0),
              environment=Environment(temperature=3.14),
              characteristics=CCDCharacteristics(qe=3, eta=4,
                                                 sv=5, amp=6,
                                                 a1=7, a2=8))

    data = om.dump(obj)

    # bias_voltage: 8.0
    assert data == """!CCD
characteristics: !ccd_characteristics
  a1: 7
  a2: 8
  amp: 6
  eta: 4
  fwc: null
  fwc_serial: null
  qe: 3
  sv: 5
environment: !environment
  temperature: 3.14
  total_ionising_dose: null
  total_non_ionising_dose: null
geometry: !ccd_geometry
  col: 1001
  material: null
  n_acceptor: 6.0
  n_donor: 7.0
  pixel_horz_size: 5.0
  pixel_vert_size: 4.0
  row: 1000
  total_thickness: 3.0
"""

# test_dumper()
