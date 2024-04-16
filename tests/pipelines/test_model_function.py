#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


import pytest
from typing_extensions import deprecated

from pyxel.detectors import CCD, CCDGeometry, Characteristics, Detector, Environment
from pyxel.pipelines import Arguments, ModelFunction


def my_func1(detector: Detector, param1: int, param2: str = "Hello") -> None:
    pass


@deprecated("only for tests")
def my_func2(detector: Detector) -> None:
    pass


# Missing 'detector'
def my_func3(param1: int, param2: str = "Hello") -> None:
    pass


@pytest.fixture
def ccd_detector() -> CCD:
    return CCD(
        geometry=CCDGeometry(row=835, col=1),
        environment=Environment(),
        characteristics=Characteristics(),
    )


def test_model_function(ccd_detector: CCD):
    """Test class 'ModelFunction'."""
    model_function = ModelFunction(
        func="test_model_function.my_func1",
        name="first_function",
        arguments={"param1": 2, "param2": "foo"},
        enabled=True,
    )

    assert repr(model_function).startswith("ModelFunction(name='first_function', ")
    assert model_function.func == my_func1
    assert model_function.name == "first_function"
    assert model_function.arguments == Arguments({"param1": 2, "param2": "foo"})
    assert model_function.enabled is True

    model_function(detector=ccd_detector)


def test_model_function_no_params(ccd_detector: CCD):
    """Test class 'ModelFunction'."""
    model_function = ModelFunction(
        func="test_model_function.my_func2",
        name="second_function",
        arguments=None,
        enabled=True,
    )

    assert repr(model_function).startswith("ModelFunction(name='second_function', ")
    assert model_function.func == my_func2
    assert model_function.name == "second_function"
    assert model_function.arguments == Arguments({})
    assert model_function.enabled is True

    model_function(detector=ccd_detector)


def test_model_function_missing_param_detector(ccd_detector: CCD):
    """Test class 'ModelFunction' with a function missing parameter 'detector'."""
    model_function = ModelFunction(
        func="test_model_function.my_func3",
        name="third_function",
        arguments={"param3": 2},
        enabled=True,
    )

    # TODO: Improve this
    with pytest.raises(TypeError):
        _ = model_function(detector=ccd_detector)


def test_model_function_missing_function():
    """Test class 'ModelFunction' with a function that should fail."""
    model_function = ModelFunction(
        func="test_model_function.unknown_func",
        name="my_func",
        arguments={"param3": 2},
        enabled=True,
    )

    with pytest.raises(ImportError):
        _ = model_function.func
