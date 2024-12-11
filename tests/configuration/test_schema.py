#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import json
from importlib import resources
from pathlib import Path

import pytest
from yaml import safe_load

# This is equivalent to 'import jsonschema'
jsonschema = pytest.importorskip(
    "jsonschema",
    reason="Package 'jsonschema' is not installed. Use 'pip install jsonschema'",
)


@pytest.fixture
def schema(request: pytest.FixtureRequest) -> dict:
    full_filename = resources.files("pyxel.static").joinpath("pyxel_schema.json")

    with full_filename.open() as fh:
        content = json.load(fh)

    jsonschema.Draft7Validator.check_schema(content)

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
