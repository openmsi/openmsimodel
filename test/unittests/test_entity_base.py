# imports
import pkg_resources, subprocess, unittest
from openmsimodel.entity.base.base_node import BaseNode


class TestEntityBaseNode(unittest.TestCase):
    def test_initialization(self):
        with self.assertRaises(TypeError):  # can't instantiate on its own
            b = BaseNode(name="base")
