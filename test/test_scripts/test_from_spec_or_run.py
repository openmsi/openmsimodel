import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")
from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.base.material import Material


class Test(unittest.TestCase):
    """this tests functions related to the subworkflow module."""

    def base_element_from_spec_or_run(self):
        # Material
        mat_from_spec = Material.from_spec_or_run(name=cake.spec.name, spec=cake.spec)
