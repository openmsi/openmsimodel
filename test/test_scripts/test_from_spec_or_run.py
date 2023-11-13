import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")
from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.helpers import from_spec_or_run
from gemd.demo import cake

import openmsimodel.stores.gemd_template_store as store_tools

store_tools.stores_config.activated = False


class TestFromSpecOrRun(unittest.TestCase):
    """this tests functions related to the subworkflow module."""

    def test_cake_mat_from_spec_succesful(self):
        cake_example = cake.make_cake(seed=42)
        mat_from_spec = from_spec_or_run(
            name=cake_example.spec.name, spec=cake_example.spec
        )
        self.assertEquals(mat_from_spec.name, cake_example.spec.name)
        # self.assertEqual( # cannot get tested in this case bc cake example doesn't have auto uids
        #     cake_example.uids["auto"],
        #     mat_from_spec.run.uids["auto"],
        # )
        # self.assertFalse("auto" in cake_example.uids)
        # self.assertTrue("auto" in mat_from_spec.run.uids) #FIXME: add auto uids to runs after they get added
        self.assertEqual(
            cake_example.spec.uids["citrine-demo"],
            mat_from_spec.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.spec.template.uids["citrine-demo-template"],
            mat_from_spec.template.uids["citrine-demo-template"],
        )

    def test_cake_mat_from_run_succesful(self):
        cake_example = cake.make_cake(seed=42)
        mat_from_run = from_spec_or_run(name=cake_example.name, run=cake_example)
        self.assertEquals(mat_from_run.name, cake_example.name)
        self.assertEqual(
            cake_example.uids["citrine-demo"],
            mat_from_run.run.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.spec.uids["citrine-demo"],
            mat_from_run.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.spec.template.uids["citrine-demo-template"],
            mat_from_run.template.uids[
                "citrine-demo-template"
            ],  # FIXME: have different auto uids
        )

    def test_cake_mat_from_spec_and_run_succesful(self):
        cake_example = cake.make_cake(seed=42)
        mat_from_spec_and_run = from_spec_or_run(
            name=cake_example.name, run=cake_example, spec=cake_example.spec
        )
        self.assertEquals(mat_from_spec_and_run.name, cake_example.name)
        self.assertEqual(
            cake_example.uids["citrine-demo"],
            mat_from_spec_and_run.run.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.spec.uids["citrine-demo"],
            mat_from_spec_and_run.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.spec.template.uids["citrine-demo-template"],
            mat_from_spec_and_run.spec.template.uids["citrine-demo-template"],
        )

    # def test_cake_mat_element_from_spec_successful(self):
    #     cake_example = cake.make_cake(seed=42)
    #     mat_from_spec = Material.from_spec_or_run(
    #         name=cake_example.spec.name, spec=cake_example.spec
    #     )
    #     self.assertEqual(
    #         cake_example.spec.uids["citrine-demo"],
    #         mat_from_spec.spec.uids["citrine-demo"],
    #     )

    # def test_cake_mat_element_from_run_successful(self):
    #     cake_example = cake.make_cake(seed=42)
    #     mat_from_run = Material.from_spec_or_run(
    #         name=cake_example.name, run=cake_example
    #     )
    #     self.assertEqual(
    #         cake_example.uids["citrine-demo"],
    #         mat_from_run.run.uids["citrine-demo"],
    #     )

    ################# Process #########################

    def test_cake_process_from_spec_succesful(self):
        cake_example = cake.make_cake(seed=42)
        process_from_spec = from_spec_or_run(
            name=cake_example.process.spec.name, spec=cake_example.process.spec
        )
        self.assertEquals(process_from_spec.name, cake_example.process.spec.name)
        self.assertEqual(
            cake_example.process.spec.uids["citrine-demo"],
            process_from_spec.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.process.spec.template.uids["citrine-demo-template"],
            process_from_spec.template.uids["citrine-demo-template"],
        )

    def test_cake_process_from_run_succesful(self):
        cake_example = cake.make_cake(seed=42)
        process_from_run = from_spec_or_run(
            name=cake_example.process.name, run=cake_example.process
        )
        self.assertEquals(process_from_run.name, cake_example.process.name)
        self.assertEqual(
            cake_example.process.uids["citrine-demo"],
            process_from_run.run.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.process.spec.uids["citrine-demo"],
            process_from_run.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.process.spec.template.uids["citrine-demo-template"],
            process_from_run.template.uids[
                "citrine-demo-template"
            ],  # FIXME: have different auto uids
        )

    def test_cake_process_from_spec_and_run_succesful(self):
        cake_example = cake.make_cake(seed=42)
        process_from_spec_and_run = from_spec_or_run(
            name=cake_example.name,
            run=cake_example.process,
            spec=cake_example.process.spec,
        )
        self.assertEquals(process_from_spec_and_run.name, cake_example.process.name)
        self.assertEqual(
            cake_example.process.uids["citrine-demo"],
            process_from_spec_and_run.run.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.process.spec.uids["citrine-demo"],
            process_from_spec_and_run.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            cake_example.process.spec.template.uids["citrine-demo-template"],
            process_from_spec_and_run.spec.template.uids["citrine-demo-template"],
        )

    ################# Measurement #########################

    def test_cake_measurement_from_spec_succesful(self):
        cake_example = cake.make_cake(seed=42)
        measurement_spec = cake_example.measurements[0].spec
        measurement_from_spec = from_spec_or_run(
            name=measurement_spec.name, spec=measurement_spec
        )
        self.assertEquals(measurement_from_spec.name, measurement_spec.name)
        self.assertEqual(
            measurement_spec.uids["citrine-demo"],
            measurement_from_spec.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            measurement_spec.template.uids["citrine-demo-template"],
            measurement_from_spec.template.uids["citrine-demo-template"],
        )

    def test_cake_measurement_from_run_succesful(self):
        cake_example = cake.make_cake(seed=42)
        measurement_run = cake_example.measurements[0]
        measurement_from_run = from_spec_or_run(
            name=measurement_run.name, run=measurement_run
        )
        self.assertEquals(measurement_from_run.name, measurement_run.name)
        self.assertEqual(
            measurement_run.uids["citrine-demo"],
            measurement_from_run.run.uids["citrine-demo"],
        )
        self.assertEqual(
            measurement_run.template.uids["citrine-demo-template"],
            measurement_from_run.template.uids["citrine-demo-template"],
        )

    def test_cake_measurement_from_spec_and_run_succesful(self):
        cake_example = cake.make_cake(seed=42)
        measurement_run = cake_example.measurements[0]
        measurement_spec = measurement_run.spec
        measurement_from_spec_and_run = from_spec_or_run(
            name=measurement_run.name, spec=measurement_spec, run=measurement_run
        )
        self.assertEquals(measurement_from_spec_and_run.name, measurement_run.name)
        self.assertEqual(
            measurement_run.uids["citrine-demo"],
            measurement_from_spec_and_run.run.uids["citrine-demo"],
        )
        self.assertEqual(
            measurement_spec.uids["citrine-demo"],
            measurement_from_spec_and_run.spec.uids["citrine-demo"],
        )
        self.assertEqual(
            measurement_spec.template.uids["citrine-demo-template"],
            measurement_from_spec_and_run.template.uids["citrine-demo-template"],
        )

    # TODO: Test when run and spec THAT ARE NOT LINKED gets passes
