#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import xarray as xr

import pyxel
from pyxel import Configuration
from pyxel.detectors import Detector


def test_basic_exposure(tmp_path: Path):
    """Functional test with a basic Exposure mode."""
    config_filename: str = "data/basic_exposure.yaml"

    current_folder = Path(__file__).parent
    config_full_filename = current_folder / config_filename
    assert config_full_filename.exists()

    # Read configuration file
    cfg = pyxel.load(config_filename)
    assert isinstance(cfg, Configuration)

    # Save 'detector' before modifications
    detector = cfg.detector
    assert isinstance(detector, Detector)

    # detector_filename_before = tmp_path / "before_detector.hdf5"
    # assert not detector_filename_before.exists()
    #
    # detector.to_hdf5(detector_filename_before)
    # assert detector_filename_before.exists()

    # Execute 'cfg'
    ds = pyxel.run_mode(
        mode=cfg.running_mode,
        detector=cfg.detector,
        pipeline=cfg.pipeline,
    )
    assert isinstance(ds, xr.Dataset)

    # Save the 'detector' object into a '.hdf5' file
    detector_filename: Path = tmp_path / "detector.hdf5"
    assert not detector_filename.exists()

    detector.to_hdf5(detector_filename)
    assert detector_filename.exists()


if __name__ == "__main__":
    from tempfile import mkdtemp

    test_basic_exposure(Path(mkdtemp(dir="/tmp")))
