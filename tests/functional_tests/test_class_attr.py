import attr
import functools


def yolo(klass):
    print('yolo:', klass)

    def _wrapper(*args, **kwargs):
        print('_wrapper:', args, kwargs)
        new_dict = {}

        # Only for testing
        new_dict['XX'] = lambda self, el: el + 1

        # Create getter/setter
        def _get_cols(self):
            print('getter:', '_cols', self._cols)
            return self._cols

        def _set_cols(self, value):
            # Do conversion + validation here
            print('setter:', '_cols', value)
            att = getattr(attr.fields(type(self)), '_cols')
            if att.validator:
                att.validator(self, att, value)
                self._cols = value

        # new_dict['_get_cols'] = _get_cols
        # new_dict['_set_cols'] = _set_cols


        #         new_dict['_set_cols'] = _set_cols
        #         new_dict['cols'] = property()


        # cols = property(_get_cols,
        #                 _set_cols,
        #                 None,
        #                 "This is the documentation2")

        setattr(klass, 'cols', property(_get_cols,
                                        _set_cols,
                                        None,
                                        "This is the documentation2"))

        obj = klass(*args, **kwargs)

        for name, value in new_dict.items():
            new_func = functools.partial(value, obj)
            # setattr(obj, name, new_func)

        return obj

    return _wrapper

import pyxel

pyxel.check_range(0, 100, 1)

x = lambda inst, att, value: pyxel.check_range(0, 100, 1)(value)


@yolo
@attr.s(repr=True)
class Test2:
    _cols = attr.ib(type=int, validator=attr.validators.instance_of(int),
                    metadata={'DOC': "This is the documentation",
                              'IS_READONLY': False})


x = Test2(cols=10)
print(x)
x.cols = 12
print(x.cols)
pass


class Test3:
    _cols = attr.ib(type=int, validator=attr.validators.instance_of(int),
                    metadata={'DOC': "This is the documentation",
                              'IS_READONLY': False})

Test3 = attr.s(repr=True)(Test3)
Test3 = yolo(Test3)

y = Test3(cols=13)
print(y.cols)
print(y)


def bar(Klass):

    def _wrapper(*args, **kwargs):
        Test4_1 = attr.s(repr=True)(Klass)
        Test4_2 = yolo(Test4_1)

        return Test4_2(*args, **kwargs)

    return _wrapper


@bar
class Test4:
    _cols = attr.ib(type=int, validator=attr.validators.instance_of(int),
                    metadata={'DOC': "This is the documentation",
                              'IS_READONLY': False})


y = Test4(cols=13)
print(y.cols)
print(y)


# Create getter/setter
def _get_getter(key, inst):
    print('getter:', key, inst._cols)
    return getattr(inst, key)


def _set_setter(key, inst, value):
    # Do conversion + validation here
    print('setter:', key, value)
    att = getattr(attr.fields(type(inst)), key)
    if att.validator:
        att.validator(inst, att, value)
        setattr(inst, key, value)
        # inst._cols = value
    # validate_func = att.metadata.get('VALIDATE')
    # if validate_func:
    #     is_valid = validate_func(value)
    #     if not is_valid:
    #         raise pyxel.ValidationError('xxx', 'arg', value)


def baz(maybe_cls=None):

    def _wrapper(Klass):

        bad_atts = {}
        for key, value in Klass.__dict__.items():
            cls_name = value.__class__.__name__
            if cls_name == '_CountingAttr':
                if not key.startswith('_'):
                    bad_atts[key] = value

        for key, bad_att in bad_atts.items():
            new_name = '_' + key
            delattr(Klass, key)
            setattr(Klass, new_name, bad_att)

        attr_klass = attr.s(repr=False, slots=False)(Klass)

        atts = attr.fields(attr_klass)
        # atts = attr.fields(Klass)
        for att in atts:
            key = att.name
            if key.startswith('_'):
                name = key.lstrip('_')
                # TODO: check for IS_READONLY => remove setter
                setattr(attr_klass, name, property(functools.partial(_get_getter, key),
                                                   functools.partial(_set_setter, key),
                                                   None,
                                                   att.metadata.get('DOC')))

        # Add method '__repr__
        def dummy_repr(self):
            return '%s(cols: %r, rows: %r)' % (type(self).__name__, self._cols, self._rows)

        setattr(attr_klass, '__repr__', dummy_repr)

        return attr_klass

    if maybe_cls is None:
        return _wrapper
    else:
        return _wrapper(maybe_cls)

    return _wrapper


# @attrs(repr=False, slots=True, hash=True)
def pyxel_validator(inst, attr, value):
    validate_func = attr.metadata.get('VALIDATE')
    if validate_func:
        is_valid = validate_func(value)
        if not is_valid:
            raise pyxel.ValidationError('xxx', 'arg', value)


@baz
class Test5:
    _cols = attr.ib(type=int, validator=pyxel_validator,
                    metadata={'DOC': "This is the cols documentation",
                              'IS_READONLY': False,
                              'VALIDATE': pyxel.check_range(0, 100, 1),
                              })

    rows = attr.ib(type=int, validator=pyxel_validator,
                    metadata={'DOC': "This is the rows documentation",
                              'IS_READONLY': False,
                              'VALIDATE': pyxel.check_range(0, 100, 1),
                              })


y = Test5(cols=13, rows=50)
print(repr(y))
z = Test5(cols=15, rows=50)
print(y.cols)
y.cols = 30
print(y.rows)
y.rows = 20

print(y)