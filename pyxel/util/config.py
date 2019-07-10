"""TBW."""

import typing as t

import esapy_config.config as config
import esapy_config.funcargs as funcargs


def detector_class(cls):
    """TBW."""
    return config.attr_class(maybe_cls=cls, init_set=True)


def attribute(doc: t.Optional[str] = None,
              is_property: t.Optional[bool] = None,
              on_set: t.Optional[t.Callable] = None,
              on_get: t.Optional[t.Callable] = None,
              on_change: t.Optional[t.Callable] = None,
              use_dispatcher: t.Optional[bool] = None,
              on_get_update: t.Optional[bool] = None,
              **kwargs):
    """TBW."""
    return config.attr_def(doc=doc,
                           is_property=is_property,
                           on_set=on_set,
                           on_get=on_get,
                           on_change=on_change,
                           use_dispatcher=use_dispatcher,
                           on_get_update=on_get_update,
                           **kwargs)


def argument(name: str, **kwargs):
    """TBW."""
    return funcargs.argument(name=name, **kwargs)
