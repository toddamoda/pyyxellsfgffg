import pytest

from pyxel.detectors.ccd_geometry import CCDGeometry
# from pyxel.io.yaml_processor import dump
# from pyxel.io.yaml_processor import load


@pytest.mark.skip(reason=None)
def test_loader():
    """Test `PyxelLoader`."""
    data = """
!ccd_geometry
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
"""
    # bias_voltage: 8.0
    obj = io.load(data)

    assert isinstance(obj, CCDGeometry)
    assert obj.row == 1000
    assert obj.col == 1001
    assert obj.depletion_thickness == 1.0
    assert obj.field_free_thickness == 2.0
    assert obj.total_thickness == 3.0
    assert obj.pixel_vert_size == 4.0
    assert obj.pixel_horz_size == 5.0
    # assert obj.material == 'foo'
    assert obj.n_acceptor == 6.0
    assert obj.n_donor == 7.0
    # assert obj.bias_voltage == 8.0


@pytest.mark.skip(reason=None)
def test_dumper():
    """Test `PyxelDumper`."""
    obj = CCDGeometry(row=1000,
                      col=1001,
                      depletion_thickness=1.0,
                      field_free_thickness=2.0,
                      total_thickness=3.0,
                      pixel_vert_size=4.0,
                      pixel_horz_size=5.0,
                      # material=foo,
                      n_acceptor=6.0,
                      n_donor=7.0)   # bias_voltage=8.0)

    # bias_voltage: 8.0
    data = io.dump(obj)
    assert data == """!ccd_geometry
col: 1001
depletion_thickness: 1.0
field_free_thickness: 2.0
material: null
n_acceptor: 6.0
n_donor: 7.0
pixel_horz_size: 5.0
pixel_vert_size: 4.0
row: 1000
total_thickness: 3.0
"""
