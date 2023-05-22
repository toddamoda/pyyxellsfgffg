#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import xarray as xr
from datatree import DataTree

import pyxel
from pyxel import Configuration
from pyxel.detectors import Detector


def test_basic_exposure_hdf5(tmp_path: Path):
    """Functional test with a basic Exposure mode."""
    config_filename: str = "tests/functional_tests/data/basic_exposure.yaml"
    config_full_filename = Path(config_filename).resolve()
    assert config_full_filename.exists()

    # Read configuration file
    cfg = pyxel.load(config_filename)
    assert isinstance(cfg, Configuration)

    # Save 'detector' before modifications
    detector = cfg.detector
    assert isinstance(detector, Detector)

    detector_filename_before = tmp_path / "before_detector.hdf5"
    assert not detector_filename_before.exists()

    detector.to_hdf5(detector_filename_before)
    assert detector_filename_before.exists()

    # Execute 'cfg'
    data_tree = pyxel.run_mode(
        mode=cfg.running_mode,
        detector=cfg.detector,
        pipeline=cfg.pipeline,
    )
    assert isinstance(data_tree, DataTree)

    # Save the 'detector' object into a '.hdf5' file
    detector_filename: Path = tmp_path / "detector.hdf5"
    assert not detector_filename.exists()

    detector.to_hdf5(detector_filename)
    assert detector_filename.exists()

    # Load to a new 'detector' object from '.hdf5' file
    new_detector = Detector.from_hdf5(detector_filename)

    assert detector.data.isomorphic(new_detector.data)
    assert set(detector.data.groups) == set(new_detector.data.groups)
    # assert detector == new_detector


def test_basic_exposure_asdf(tmp_path: Path):
    """Functional test with a basic Exposure mode."""
    config_filename: str = "tests/functional_tests/data/basic_exposure.yaml"
    config_full_filename = Path(config_filename).resolve()
    assert config_full_filename.exists()

    # Read configuration file
    cfg = pyxel.load(config_filename)
    assert isinstance(cfg, Configuration)

    # Save 'detector' before modifications
    detector = cfg.detector
    assert isinstance(detector, Detector)

    detector_filename_before = tmp_path / "before_detector.asdf"
    assert not detector_filename_before.exists()

    detector.to_asdf(detector_filename_before)
    assert detector_filename_before.exists()

    # Execute 'cfg'
    data_tree = pyxel.run_mode(
        mode=cfg.running_mode,
        detector=cfg.detector,
        pipeline=cfg.pipeline,
    )
    assert isinstance(data_tree, DataTree)

    # Save the 'detector' object into a '.asdf' file
    detector_filename: Path = tmp_path / "detector.asdf"
    assert not detector_filename.exists()

    detector.to_asdf(detector_filename)
    assert detector_filename.exists()

    # Load to a new 'detector' object from '.asdf' file
    new_detector = Detector.from_asdf(detector_filename)

    assert detector.data.isomorphic(new_detector.data)
    assert set(detector.data.groups) == set(new_detector.data.groups)
    # assert detector == new_detector
