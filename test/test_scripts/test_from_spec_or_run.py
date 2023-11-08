import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")
from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.helpers import from_spec_or_run
from gemd.demo import cake


class TestFromSpecOrRun(unittest.TestCase):
    """this tests functions related to the subworkflow module."""

    def test_cake_from_spec_or_run_succesful(self):
        cake_example = cake.make_cake(seed=42)
        mat_from_spec = from_spec_or_run(
            name=cake_example.spec.name, spec=cake_example.spec
        )
        self.assertEqual(
            cake_example.spec.uids["citrine-demo"],
            mat_from_spec.spec.uids["citrine-demo"],
        )

    def test_cake_base_element_from_spec_or_run_successful(self):
        cake_example = cake.make_cake(seed=42)
        mat_from_spec = Material.from_spec_or_run(
            name=cake_example.spec.name, spec=cake_example.spec
        )
        self.assertEqual(
            cake_example.spec.uids["citrine-demo"],
            mat_from_spec.spec.uids["citrine-demo"],
        )
