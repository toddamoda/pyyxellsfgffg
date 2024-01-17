#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import pytest

import pyxel


def test_bad_observation_custom_mode(monkeypatch: pytest.MonkeyPatch):
    """Test Observation custom mode with a bad custom file."""
    base_path = Path(__file__).parent
    monkeypatch.chdir(base_path)

    config_filename = Path("data/bad_observation_custom.yaml").resolve()
    assert config_filename.exists()

    with pytest.raises(ValueError, match=r"Custom data file has"):
        _ = pyxel.load(config_filename)


def test_good_observation_custom_mode(monkeypatch: pytest.MonkeyPatch):
    """Test Observation custom mode with a bad custom file."""
    base_path = Path(__file__).parent
    monkeypatch.chdir(base_path)

    config_filename = Path("data/good_observation_custom.yaml").resolve()
    assert config_filename.exists()

    _ = pyxel.load(config_filename)
