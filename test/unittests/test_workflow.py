import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")
from openmsimodel.workflow.workflow import Workflow


class TestWorkflow(unittest.TestCase):
    """this tests functions related to the subworkflow module."""

    def test_workflow_instantiation(self):
        w = Workflow()