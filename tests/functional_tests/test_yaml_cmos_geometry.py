import pytest

from pyxel.detectors.cmos_geometry import CMOSGeometry
import esapy_config.io as io


@pytest.mark.skip(reason=None)
def test_loader():
    """Test `PyxelLoader`."""
    data = """
!cmos_geometry
 row: 1000
 col: 1001
 total_thickness: 3.0
 pixel_vert_size: 4.0
 pixel_horz_size: 5.0
 material: hxrg
 n_acceptor: 6.0
 n_donor: 7.0
 n_output: 9
 n_row_overhead: 10
 n_frame_overhead: 11
 reverse_scan_direction: true
 reference_pixel_border_width: 12
"""

    obj = io.load(data)

    assert isinstance(obj, CMOSGeometry)
    assert obj.row == 1000
    assert obj.col == 1001
    assert obj.total_thickness == 3.0
    assert obj.pixel_vert_size == 4.0
    assert obj.pixel_horz_size == 5.0
    # assert obj.material == 'foo'
    assert obj.n_acceptor == 6.0
    assert obj.n_donor == 7.0
    # assert obj.bias_voltage == 8.0
    assert obj.n_output == 9
    assert obj.n_row_overhead == 10
    assert obj.n_frame_overhead == 11
    assert obj.reverse_scan_direction is True
    assert obj.reference_pixel_border_width == 12


@pytest.mark.skip(reason=None)
def test_dumper():
    """Test `PyxelDumper`."""
    obj = CMOSGeometry(row=1000,
                       col=1001,
                       total_thickness=3.0,
                       pixel_vert_size=4.0,
                       pixel_horz_size=5.0,
                       # material=foo,
                       n_acceptor=6.0,
                       n_donor=7.0,
                       # bias_voltage=8.0,
                       n_output=9,
                       n_row_overhead=10,
                       n_frame_overhead=11,
                       reverse_scan_direction=True,
                       reference_pixel_border_width=1)

    # bias_voltage: 8.0
    data = io.dump(obj)
    assert data == """!cmos_geometry

col: 1001
material: null
n_acceptor: 6.0
n_donor: 7.0
n_frame_overhead: 11
n_output: 9
n_row_overhead: 10
pixel_horz_size: 5.0
pixel_vert_size: 4.0
reference_pixel_border_width: 1
reverse_scan_direction: true
row: 1000
total_thickness: 3.0
"""
# bias_voltage: 8.0
