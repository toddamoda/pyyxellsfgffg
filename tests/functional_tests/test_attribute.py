import attr
import esapy_config as om


@om.attr_class
class MyClass1:
    _cols = attr.ib(type=int,
                    validator=om.validate_range(0, 100, 1, is_optional=True),
                    default=None,
                    metadata={'doc': "This is the cols documentation",
                              'readonly': False,
                              })

    rows = om.attr_def(type=int,
                       default=None,
                       doc="This is the rows documentation",
                       readonly=False,
                       validator=[om.validate_type(int, is_optional=True),
                                  om.validate_range(0, 100, 1, is_optional=True)
                                  ]
                       )

    width = attr.ib(type=int,
                    validator=[attr.validators.instance_of(int), om.validate_range(0, 100, 1)],
                    default=0,
                    metadata={'doc': "This is the rows documentation",
                              'readonly': False,
                              })

    height = om.attr_def(type=int,
                         default=None,
                         converter=om.optional(int),
                         doc="This is the rows documentation",
                         readonly=False,
                         validator=om.validate_range(0, 100, 1, is_optional=True))


# @pytest.mark.skip(reason="not working for some strange reason")
def test_attr_class():

    #
    # Test None default attribute value initializer
    #
    obj = MyClass1()
    assert obj.cols is None
    assert obj.rows is None

    #
    # Test setter and getter for _cols (with underscore)
    #
    obj.cols = 10
    assert obj.cols == 10
    assert obj._cols == 10

    #
    # Test setter and getter for rows (no underscore)
    #
    obj.rows = 20
    assert obj.rows == 20
    assert obj._rows == 20

    #
    # Test attr instance_of validator
    #
    obj.width = 1
    exc_caught = None
    try:
        obj.width = 0.1
    except TypeError as exc:
        exc_caught = exc
    finally:
        assert isinstance(exc_caught, TypeError)

    #
    # Test 'validate' metadata validator
    #
    exc_caught = None
    try:
        obj.rows = 1.5
    except om.ValidationError as exc:
        exc_caught = exc
    except om.validators.errors.ValidationError as exc:
        exc_caught = exc
    finally:
        assert isinstance(exc_caught, om.ValidationError) or \
                   isinstance(exc_caught, om.validators.errors.ValidationError)

    #
    # Test 'cast' functionality.
    #
    obj.height = 1.5
    assert obj.height == 1

    #
    # Test check_range validator
    #
    att_rows = next(att for att in attr.fields(MyClass1) if att.name == '_rows')
    # att_rows.metadata['cast'] = True  # This does not work. mappingproxy is immutable
    info = om.get_validate_info(att_rows.validator._validators[1])
    assert info['min_val'] == 0
    assert info['max_val'] == 100
    obj.rows = info['min_val']  # check limits
    obj.rows = info['max_val']

    exc_caught = None
    try:
        obj.rows = info['max_val'] + 1
    except om.ValidationError as exc:
        exc_caught = exc
    except om.validators.errors.ValidationError as exc:
        exc_caught = exc
    finally:
        assert isinstance(exc_caught, om.ValidationError) or \
               isinstance(exc_caught, om.validators.errors.ValidationError)
