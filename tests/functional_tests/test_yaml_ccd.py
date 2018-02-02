from pyxel.detectors.ccd import CCD
from pyxel.pipelines.yaml_processor import dump
from pyxel.pipelines.yaml_processor import load


def test_loader():
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
    k: 1
    j: 2
    qe: 3
    eta: 4
    sv: 5
    accd: 6
    a1: 7
    a2: 8
"""

    obj = load(data)

    assert isinstance(obj, CCD)
