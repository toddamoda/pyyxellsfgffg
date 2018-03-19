"""TBW."""
import functools
import attr
import typing as t

from . import validator


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
    value = cast_value(inst, att, value)
    if att.validator:
        att.validator(inst, att, value)
    setattr(inst, key, value)


def attr_def(doc: str=None,
             readonly: bool=False,
             label: str=None,
             units: str=None,
             validate: t.Callable=None,
             cast: bool=False,
             *args, **kwargs):
    """Class attribute definition.

    :param doc:
    :param readonly:
    :param label:
    :param units:
    :param validate:
    :param cast: if set to True, automatically convert the value to the type.
    :param args: arguments sent to attr.ib
    :param kwargs: keyword arguments sent to attr.ib
    :return:
    """
    metadata = kwargs.get('metadata', {})
    metadata['validate'] = validate
    metadata['doc'] = doc
    metadata['readonly'] = readonly
    metadata['label'] = label
    metadata['units'] = units
    metadata['cast'] = cast

    kwargs['metadata'] = metadata

    if 'validator' not in kwargs and validate:
        kwargs['validator'] = att_validator

    attrib = attr.ib(*args, **kwargs)

    return attrib


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
        for attrib in atts:
            key = attrib.name
            if key.startswith('_'):
                name = key.lstrip('_')
                # TODO: check for IS_READONLY => remove setter
                setattr(attr_klass, name, property(functools.partial(_get_getter, key),
                                                   functools.partial(_set_setter, key),
                                                   None,
                                                   attrib.metadata.get('DOC')))

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


def cast_value(inst, attrib, value):
    """TBW.

    :param inst:
    :param attrib:
    :param value:
    :return:
    """
    if attrib.type and not isinstance(value, attrib.type) and attrib.metadata.get('cast', False):
        try:
            value = attrib.type(value)
        except ValueError as cast_exc:
            msg = 'Cast Error: ' + str(cast_exc)
            raise validator.ValidationError(inst.__class__, attrib.name, value, msg)
    return value


def check_type(inst, attrib, value):
    """TBW.

    :param inst:
    :param attrib:
    :param value:
    :return:
    """
    if attrib.type and not isinstance(value, attrib.type):
        msg = 'Type Error: {name!r} must be {type!r} (got {value!r} that is a {actual!r}).'
        msg = msg.format(name=attrib.name, type=attrib.type, actual=value.__class__, value=value)
        raise validator.ValidationError(inst.__class__, attrib.name, value, msg)


def att_validator(inst, attrib, value):
    """TBW.

    :param inst:
    :param attrib:
    :param value:
    :return:
    """
    validator_func = attrib.metadata.get('validate')
    if value is None and attrib.default is None:
        return

    value = cast_value(inst, attrib, value)
    check_type(inst, attrib, value)

    if validator_func:
        extra_info = validator.get_validate_info(validator_func)
        msg = extra_info['error_message'].format(value)

        try:
            is_valid = validator_func(value)
        except Exception as other_exc:
            msg += 'Exception: ' + str(other_exc)
            is_valid = False

        if not is_valid:
            exc = validator.ValidationError(inst.__class__, attrib.name, value, msg)
            raise exc
