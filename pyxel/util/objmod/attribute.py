"""TBW."""
import functools
import attr
import typing as t

from .validator import ValidationError


# Create getter/setter
def _get_getter(key, inst):
    """TBW.

    :param key:
    :param inst:
    :return:
    """
    # print('getter:', key, inst._cols)
    return getattr(inst, key)


def _set_setter(key, inst, value):
    """TBW.

    :param key:
    :param inst:
    :param value:
    :return:
    """
    # Do conversion + validation here
    # print('setter:', key, value)
    att = getattr(attr.fields(type(inst)), key)
    if att.validator:
        att.validator(inst, att, value)
    setattr(inst, key, value)


def attr_def(doc: str=None, readonly: bool=False, label: str=None, units: str=None, check: t.Callable=None,
             *args, **kwargs):
    """Class attribute definition.

    :param doc:
    :param readonly:
    :param label:
    :param units:
    :param check:
    :param args: arguments sent to attr.ib
    :param kwargs: keyword arguments sent to attr.ib
    :return:
    """
    metadata = kwargs.get('metadata', {})
    metadata['validate'] = check
    metadata['doc'] = doc
    metadata['readonly'] = readonly
    metadata['label'] = label
    metadata['units'] = units

    kwargs['metadata'] = metadata

    att = attr.ib(*args, **kwargs)

    return att


def attr_class(maybe_cls=None):
    """TBW.

    :param maybe_cls:
    :return:
    """
    def _wrapper(klass):
        """TBW.

        :param klass:
        :return:
        """
        bad_atts = {}
        for key, value in klass.__dict__.items():
            cls_name = value.__class__.__name__
            if cls_name == '_CountingAttr':
                if not key.startswith('_'):
                    bad_atts[key] = value

        for key, bad_att in bad_atts.items():
            new_name = '_' + key
            delattr(klass, key)
            setattr(klass, new_name, bad_att)

        attr_klass = attr.s(repr=False, slots=False)(klass)

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
def meta_validator(inst, attrib, value):
    """TBW.

    :param inst:
    :param attrib:
    :param value:
    :return:
    """
    validate_func = attr.metadata.get('VALIDATE')
    if validate_func:
        is_valid = validate_func(value)
        if not is_valid:
            raise ValidationError('xxx', 'arg', value)

#
# @baz
# class Test5:
#     _cols = attr.ib(type=int, validator=pyxel_validator,
#                     metadata={'DOC': "This is the cols documentation",
#                               'IS_READONLY': False,
#                               'VALIDATE': check_range(0, 100, 1),
#                               })
#
#     rows = attr.ib(type=int, validator=pyxel_validator,
#                     metadata={'DOC': "This is the rows documentation",
#                               'IS_READONLY': False,
#                               'VALIDATE': check_range(0, 100, 1),
#                               })
