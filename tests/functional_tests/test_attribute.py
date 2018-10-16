import attr
# import pytest

import esapy_config as om
# from esapy_config.attribute import att_validator

# from pyxel.util import objmod as om
# from pyxel.util.objmod.attribute import att_validator


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
    finally:
        assert isinstance(exc_caught, om.ValidationError)

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
    finally:
        assert isinstance(exc_caught, om.ValidationError)

    # setattr(obj, 'cols', 11)


if __name__ == '__main__':
    test_attr_class()

# import attr
# import pyxel
# from pyxel.util import objmod as om
#
# #
# #
# # def attr_validate(instance, attribute, value):
# #     if 'validate' in attribute.metadata:
# #         return attribute.metadata['validate'](value)
# #     return True
# #
# # @property
# # def row(self, key, value):
# #     if key in self.__dict__:
# #         # handle the attribute assignment case
# #         att = getattr(attr.fields(TestAttr), key)
# #         if att:
# #             if att.type and not isinstance(value, att.type):
# #                 value = att.type(value)
# #
# #             if att.metadata:
# #                 result = att.validator(self, att, value)
# #                 print(result)
# #
# #     # if key in self.__dict__:
# #     super(TestAttr, self).__setattr__(key, value)
# #
# #
# #
# # def class_attr(cls, *arg, **kwargs):
# #
# #     @attr.s(cls)
# #     def _wrapper(*arg2, **kwargs2):
# #         # return attr.s(cls, *arg, **kwargs)
# #         # make_asstr = attr.s(cls)
# #         #
# #         # make_attr.__setattr__ = some_function
# #         return kwargs2
# #
# #     return _wrapper
#
#
# #
# # @attr.s
# # class TestAttr:
# #
# #     rows = attr.ib()  #validator=attr_validate, type=int, metadata={'validate': pyxel.check_range(2, 100, 2)})
# #     cols = attr.ib()
# #
# #     def __init__(self, rows: int, cols: int):
# #         self.rows = rows
# #         self.cols = cols
# #
# #     def __setattr__(self, key, value):
# #         if key in self.__dict__:
# #             # handle the attribute assignment case
# #             att = getattr(attr.fields(TestAttr), key)
# #             if att:
# #                 if att.type and not isinstance(value, att.type):
# #                     value = att.type(value)
# #
# #                 if att.metadata:
# #                     result = att.validator(self, att, value)
# #                     print(result)
# #
# #         # if key in self.__dict__:
# #         super(TestAttr, self).__setattr__(key, value)
# #
# #
# # x = TestAttr(rows=10, cols=12)
# # x.rows = '2'
# #
# # atts = {}
# #
# #
# # def attribute(key, validate):
# #
# #     def _wrapper(self, **kwargs):
# #         return self
# #         # return func(self, **kwargs)
# #
# #     return _wrapper
# #
# #
# # @attribute('rows', validate=pyxel.check_range(2, 100, 2))
# # @attribute('cols', validate=pyxel.check_range(2, 100, 2))
# # class Test:
# #
# #     def __init__(self, rows=None, cols=None):
# #         self.rows = rows
# #         self.cols = cols
# #
# #     def __setattr__(self, key, value):
# #         super(Test, self).__setattr__(key, value)
# #
# #
# # x = Test(rows=10, cols=10)
# # x.rows = 10
# #
#
#
# # def setattr_obj(self, key, value):
# #     if key in self.__dict__:
# #         # handle the attribute assignment case
# #         att = getattr(attr.fields(type(self)), key)
# #         if att:
# #             is_valid = True
# #             if att.type and not isinstance(value, att.type):
# #                 value = att.type(value)
# #
# #             if att.validator:
# #                 is_valid = att.validator(self, att, value)
# #
# #             validate_func = att.metadata.get('validate')
# #             if validate_func:
# #                 is_valid = validate_func(value)
# #
# #             if not is_valid:
# #                 print('Invalid setting. Attribute: %r, Value: %r' % (key, value))
# #
# #     # if key in self.__dict__:
# #     super(type(self), self).__setattr__(key, value)
# #
# #
# # def classinit(cls, *args, **kwargs):
# #
# #     def _wrapper(*arg2, **kwargs2):
# #
# #         ret = cls(**kwargs2)
# #
# #         setattr(cls, '__setattr__', setattr_obj)
# #         # ret.__setattr__ = setattr_obj
# #         return ret
# #
# #     return _wrapper
# #
# #
# # def attribute(doc=None, readonly=False, label=None, validate=None, *args, **kwargs):
# #     metadata = kwargs.get('metadata', {})
# #     metadata['validate'] = validate
# #     metadata['doc'] = doc
# #     metadata['readonly'] = readonly
# #     metadata['label'] = label
# #
# #     kwargs['metadata'] = metadata
# #
# #     att = attr.ib(*args, **kwargs)
# #
# #     return att
# #
# #
# # @classinit
# # @attr.s
# # class Test2:
# #
# #     rows = attribute(validate=pyxel.check_range(2, 100, 2))
# #     # rows = attribute(metadata={'validate': pyxel.check_range(2, 100, 2)})
# #     cols = attribute(type=int)
# #     # rows = attribute(validate=pyxel.check_range(2, 100, 2), label='', doc='', readonly=True)
# #     # cols = attribute(validate=pyxel.check_range(2, 100, 2), type=int)
# #
# #
# # y = Test2(rows=10, cols=10)
# # y.rows = 20
# # y.cols = '2'
# # print(y)
#
#
# def setattr_obj(self, key, value):
#     if key in self.__dict__:
#         # handle the attribute assignment case
#         att = getattr(attr.fields(type(self)), key)
#         if att:
#             is_valid = True
#             if att.type and not isinstance(value, att.type):
#                 value = att.type(value)
#
#             if att.validator:
#                 is_valid = att.validator(self, att, value)
#
#             validate_func = att.metadata.get('validate')
#             if validate_func:
#                 is_valid = validate_func(value)
#
#             if not is_valid:
#                 print('Invalid setting. Attribute: %r, Value: %r' % (key, value))
#
#     # if key in self.__dict__:
#     super(type(self), self).__setattr__(key, value)
#
#
# def classinit(cls, *args, **kwargs):
#
#     def _wrapper(*arg2, **kwargs2):
#         ret = cls(**kwargs2)
#
#         # setattr(cls, '__setattr__', setattr_obj)
#         # ret.__setattr__ = setattr_obj
#         return ret
#
#     return _wrapper
#
#
# def attribute(doc=None, readonly=False, label=None, validate=None, *args, **kwargs):
#     metadata = kwargs.get('metadata', {})
#     metadata['validate'] = validate
#     metadata['doc'] = doc
#     metadata['readonly'] = readonly
#     metadata['label'] = label
#
#     kwargs['metadata'] = metadata
#
#     att = attr.ib(*args, **kwargs)
#
#     return att
#
#
# @classinit
# class Test2:
#     # __setattr__ = setattr_obj
#     cols = attribute(type=int)
#     rows = attribute(validate=om.check_range(2, 100, 2), default=None, init=True)
#
#
# y = Test2(rows=10, cols=10)
# # Test2.__setattr__ = setattr_obj
# y.rows = 20
# y.cols = '2'
#
# # @attr.s
# # class BaseClass:
# #
# #     # __setattr__ = setattr_obj
# #     height = attribute(type=int)
# #     width = attribute(type=int)
# #
# #     def __setattr__(self, key, value):
# #         if key in self.__dict__:
# #             # handle the attribute assignment case
# #             att = getattr(attr.fields(type(self)), key)
# #             if att:
# #                 is_valid = True
# #                 if att.type and not isinstance(value, att.type):
# #                     value = att.type(value)
# #
# #                 if att.validator:
# #                     is_valid = att.validator(self, att, value)
# #
# #                 validate_func = att.metadata.get('validate')
# #                 if validate_func:
# #                     is_valid = validate_func(value)
# #
# #                 if not is_valid:
# #                     print('Invalid setting. Attribute: %r, Value: %r' % (key, value))
# #         super(BaseClass, self).__setattr__(key, value)
#
# # @attr.s
# # class Test2(BaseClass):
# #     # __setattr__ = setattr_obj
# #     cols = attribute(type=int)
# #     rows = attribute(validate=pyxel.check_range(2, 100, 2), default=None, init=True)
# #
# #
# # y = Test2(height=5, width=23, cols=10)
# # # Test2.__setattr__ = setattr_obj
# # y.rows = 20
# # y.cols = '2'
# # print(y)
