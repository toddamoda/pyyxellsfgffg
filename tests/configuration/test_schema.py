#  Copyright (c) European Space Agency, 2017.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import json
from pathlib import Path

import jsonschema
import pytest
from jsonschema import Draft7Validator
from yaml import safe_load


@pytest.fixture
def schema(request: pytest.FixtureRequest) -> dict:
    filename: Path = request.path.parent / "../../static/pyxel_schema.json"
    full_filename = filename.resolve(strict=True)

    with full_filename.open() as fh:
        content = json.load(fh)

    Draft7Validator.check_schema(content)

    return content


@pytest.mark.parametrize(
    "filename",
    [
        "data/calibration.yaml",
        "data/exposure1.yaml",
        "data/exposure2.yaml",
        "data/observation_custom.yaml",
        "data/observation_custom_parallel.yaml",
        "data/observation_product.yaml",
        "data/observation_sequential.yaml",
    ],
)
def test_validate_configuration_file(
    filename: str, schema: dict, request: pytest.FixtureRequest
):
    """Use a JSON schema to validate a YAML configuration file."""
    folder: Path = request.path.parent

    full_filename = folder / filename
    assert full_filename.exists()

    content: str = full_filename.read_text()

    data = safe_load(content)

    jsonschema.validate(data, schema=schema)
