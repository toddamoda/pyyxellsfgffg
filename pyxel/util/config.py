#   --------------------------------------------------------------------------
#   Copyright 2016 SRE-F, ESA (European Space Agency)
#       Hans Smit <Hans.Smit@esa.int>
#       Frederic Lemmel <Frederic.Lemmel@esa.int>
#   --------------------------------------------------------------------------
""" Utility module to aid in loading in a configuration file. """

from configparser import ConfigParser, ExtendedInterpolation
import yaml
from pathlib import Path


def extend_interpolate_yaml(obj, parent_key='', flat=None):
    if flat is None:
        flat = {}
    for key in obj:
        if isinstance(obj[key], dict):
            extend_interpolate_yaml(obj[key], key, flat)
        elif isinstance(obj[key], str):
            obj[key] = obj[key].format(**flat)
            flat[parent_key + '/' + key] = obj[key]
    return flat


def load_yaml(path):
    """ Load yaml file. """
    with open(path, 'r') as file_obj:
        cfg = yaml.load(file_obj)
        extend_interpolate_yaml(cfg)
        return cfg


def load_ini(path):
    """ Load ini file. """
    with open(path, 'r') as file_obj:
        cfg = ConfigParser(interpolation=ExtendedInterpolation())
        cfg.read_file(file_obj)
        return cfg


def load(config_path):
    """

    :param Path config_path:
    :return:
    """
    pth = Path(config_path)
    if not pth.is_file():
        raise ValueError('Expected file')

    if pth.suffix.lower() in ['.yaml', '.yml']:
        return load_yaml(pth)
    else:
        return load_ini(pth)
