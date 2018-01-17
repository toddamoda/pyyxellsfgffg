""" Unit tests for the config module """

import unittest
from pathlib import Path

import pyxel

from pyxel.util import config

# ROOT_DIR = Path(pyxel.__file__).parent.parent
ROOT_DIR = Path(__file__).parent


class TestConfig(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # def test_config(self):
    #     ini_file = ROOT_DIR.joinpath('test_config.ini')
    #     result_ini = config.load(ini_file)
    #
    #     yml_file = ROOT_DIR.joinpath('test_config.yaml')
    #     result_yml = config.load(yml_file)
    #
    #     expected = './examples/data'
    #
    #     self.assertEqual(len(result_ini.sections()), 2)
    #     self.assertListEqual(result_ini.sections(), list(result_yml.keys()))
    #     self.assertEqual(result_ini['common']['input_dir'], expected)
    #     self.assertEqual(result_yml['common']['input_dir'], expected)
