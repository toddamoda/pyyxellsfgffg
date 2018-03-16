import attr
import pyxel
#
#
# def attr_validate(instance, attribute, value):
#     if 'validate' in attribute.metadata:
#         return attribute.metadata['validate'](value)
#     return True
#
# @property
# def row(self, key, value):
#     if key in self.__dict__:
#         # handle the attribute assignment case
#         att = getattr(attr.fields(TestAttr), key)
#         if att:
#             if att.type and not isinstance(value, att.type):
#                 value = att.type(value)
#
#             if att.metadata:
#                 result = att.validator(self, att, value)
#                 print(result)
#
#     # if key in self.__dict__:
#     super(TestAttr, self).__setattr__(key, value)
#
#
#
# def class_attr(cls, *arg, **kwargs):
#
#     @attr.s(cls)
#     def _wrapper(*arg2, **kwargs2):
#         # return attr.s(cls, *arg, **kwargs)
#         # make_asstr = attr.s(cls)
#         #
#         # make_attr.__setattr__ = some_function
#         return kwargs2
#
#     return _wrapper


#
# @attr.s
# class TestAttr:
#
#     rows = attr.ib()  #validator=attr_validate, type=int, metadata={'validate': pyxel.check_range(2, 100, 2)})
#     cols = attr.ib()
#
#     def __init__(self, rows: int, cols: int):
#         self.rows = rows
#         self.cols = cols
#
#     def __setattr__(self, key, value):
#         if key in self.__dict__:
#             # handle the attribute assignment case
#             att = getattr(attr.fields(TestAttr), key)
#             if att:
#                 if att.type and not isinstance(value, att.type):
#                     value = att.type(value)
#
#                 if att.metadata:
#                     result = att.validator(self, att, value)
#                     print(result)
#
#         # if key in self.__dict__:
#         super(TestAttr, self).__setattr__(key, value)
#
#
# x = TestAttr(rows=10, cols=12)
# x.rows = '2'
#
# atts = {}
#
#
# def attribute(key, validate):
#
#     def _wrapper(self, **kwargs):
#         return self
#         # return func(self, **kwargs)
#
#     return _wrapper
#
#
# @attribute('rows', validate=pyxel.check_range(2, 100, 2))
# @attribute('cols', validate=pyxel.check_range(2, 100, 2))
# class Test:
#
#     def __init__(self, rows=None, cols=None):
#         self.rows = rows
#         self.cols = cols
#
#     def __setattr__(self, key, value):
#         super(Test, self).__setattr__(key, value)
#
#
# x = Test(rows=10, cols=10)
# x.rows = 10
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
#
#         ret = cls(**kwargs2)
#
#         setattr(cls, '__setattr__', setattr_obj)
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
# @attr.s
# class Test2:
#
#     rows = attribute(validate=pyxel.check_range(2, 100, 2))
#     # rows = attribute(metadata={'validate': pyxel.check_range(2, 100, 2)})
#     cols = attribute(type=int)
#     # rows = attribute(validate=pyxel.check_range(2, 100, 2), label='', doc='', readonly=True)
#     # cols = attribute(validate=pyxel.check_range(2, 100, 2), type=int)
#
#
# y = Test2(rows=10, cols=10)
# y.rows = 20
# y.cols = '2'
# print(y)


def setattr_obj(self, key, value):
    if key in self.__dict__:
        # handle the attribute assignment case
        att = getattr(attr.fields(type(self)), key)
        if att:
            is_valid = True
            if att.type and not isinstance(value, att.type):
                value = att.type(value)

            if att.validator:
                is_valid = att.validator(self, att, value)

            validate_func = att.metadata.get('validate')
            if validate_func:
                is_valid = validate_func(value)

            if not is_valid:
                print('Invalid setting. Attribute: %r, Value: %r' % (key, value))

    # if key in self.__dict__:
    super(type(self), self).__setattr__(key, value)


def classinit(cls, *args, **kwargs):

    def _wrapper(*arg2, **kwargs2):
        ret = cls(**kwargs2)

        # setattr(cls, '__setattr__', setattr_obj)
        # ret.__setattr__ = setattr_obj
        return ret

    return _wrapper


def attribute(doc=None, readonly=False, label=None, validate=None, *args, **kwargs):
    metadata = kwargs.get('metadata', {})
    metadata['validate'] = validate
    metadata['doc'] = doc
    metadata['readonly'] = readonly
    metadata['label'] = label

    kwargs['metadata'] = metadata

    att = attr.ib(*args, **kwargs)

    return att


@classinit
class Test2:
    # __setattr__ = setattr_obj
    cols = attribute(type=int)
    rows = attribute(validate=pyxel.check_range(2, 100, 2), default=None, init=True)


y = Test2(rows=10, cols=10)
# Test2.__setattr__ = setattr_obj
y.rows = 20
y.cols = '2'

# @attr.s
# class BaseClass:
#
#     # __setattr__ = setattr_obj
#     height = attribute(type=int)
#     width = attribute(type=int)
#
#     def __setattr__(self, key, value):
#         if key in self.__dict__:
#             # handle the attribute assignment case
#             att = getattr(attr.fields(type(self)), key)
#             if att:
#                 is_valid = True
#                 if att.type and not isinstance(value, att.type):
#                     value = att.type(value)
#
#                 if att.validator:
#                     is_valid = att.validator(self, att, value)
#
#                 validate_func = att.metadata.get('validate')
#                 if validate_func:
#                     is_valid = validate_func(value)
#
#                 if not is_valid:
#                     print('Invalid setting. Attribute: %r, Value: %r' % (key, value))
#         super(BaseClass, self).__setattr__(key, value)

# @attr.s
# class Test2(BaseClass):
#     # __setattr__ = setattr_obj
#     cols = attribute(type=int)
#     rows = attribute(validate=pyxel.check_range(2, 100, 2), default=None, init=True)
#
#
# y = Test2(height=5, width=23, cols=10)
# # Test2.__setattr__ = setattr_obj
# y.rows = 20
# y.cols = '2'
# print(y)




