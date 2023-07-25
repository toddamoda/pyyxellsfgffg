import pytest
import xarray as xr
from datatree import DataTree
from joblib.testing import warns
import pytest
import numpy as np

from pyxel.data_structure import pixel
from pyxel.detectors import (
    CCD,
    CCDGeometry,
    Characteristics,
    Environment,
    ReadoutProperties,
)
from pyxel.models.data_processing import source_extractor


@pytest.mark.parametrize("array_type,exp_warn", [("pixel", "pixel data array is empty"),
                                                 ("signal", "signal data array is empty"),
                                                 ("image", "image data array is empty"),
                                                 ("photon", "photon data array is empty"),
                                                 ("charge", "charge data array is empty")])
def test_extract_roi_to_xarray_empty_array(ccd_10x10: CCD, array_type, exp_warn):
    """Tests empty array warning"""
    with pytest.warns(UserWarning, match=exp_warn):
        source_extractor.extract_roi_to_xarray(ccd_10x10, array_type=array_type)


@pytest.fixture
def ccd_10x10() -> CCD:
    """Create a valid CCD detector."""
    detector = CCD(
        geometry=CCDGeometry(
            row=10,
            col=10,
            total_thickness=40.0,
            pixel_vert_size=10.0,
            pixel_horz_size=10.0,
        ),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    detector._readout_properties = ReadoutProperties(num_steps=1)
    return detector


def test_extract_roi_to_xarray_pixel(ccd_10x10: CCD):
    ccd_10x10.pixel.array = np.full(fill_value=1,shape=(10,10),dtype=float)
    source_extractor.extract_roi_to_xarray(ccd_10x10, array_type='pixel')

def test_extract_roi_to_xarray_signal(ccd_10x10: CCD):
    ccd_10x10.signal.array = np.full(fill_value=1,shape=(10,10),dtype=float)
    source_extractor.extract_roi_to_xarray(ccd_10x10, array_type='signal')

def test_extract_roi_to_xarray_image(ccd_10x10: CCD):
    ccd_10x10.image.array = np.full(fill_value=1,shape=(10,10),dtype=np.uint64)
    source_extractor.extract_roi_to_xarray(ccd_10x10, array_type='image')

def test_extract_roi_to_xarray_photon(ccd_10x10: CCD):
    ccd_10x10.photon.array = np.full(fill_value=1,shape=(10,10),dtype=float)
    source_extractor.extract_roi_to_xarray(ccd_10x10, array_type='photon')

def test_extract_roi_to_xarray_charge(ccd_10x10: CCD):
    ccd_10x10.charge.add_charge_array(np.full(fill_value=1,shape=(10,10),dtype=float))
    source_extractor.extract_roi_to_xarray(ccd_10x10, array_type='charge')
#     #assert np.any(ccd_10x10.pixel.array != 0)
#     """Test to ensure warning isn't triggered for filled array"""

def test_extract_roi_to_xarray_incorrect_array_type(ccd_10x10: CCD, array_type='test'):
    ccd_10x10.pixel.array = np.random.rand(10, 10)
    """Test to ensure warning isn't triggered for filled array"""

    with pytest.raises(ValueError) as x:
        source_extractor.extract_roi_to_xarray(ccd_10x10,array_type='test')
        assert str(x.value) == "Incorrect array_type. Must be one of 'pixel','signal','image',photon' or 'charge'."
