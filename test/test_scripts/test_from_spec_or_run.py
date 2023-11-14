import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")
from openmsimodel.workflow.workflow import Workflow
from openmsimodel.subworkflow.process_block import ProcessBlock
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.entity.gemd.helpers import from_spec_or_run
from gemd import ProcessTemplate, MaterialTemplate, MeasurementTemplate
import openmsimodel.stores.gemd_template_store as store_tools

store_tools.stores_config.activated = False

from gemd.demo import cake


class TestFromSpecOrRun(unittest.TestCase):
    """this tests functions related to the subworkflow module."""

    def test_cake_mat_from_spec_successful(self):
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

    def test_cake_mat_from_run_successful(self):
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

    def test_cake_mat_from_spec_and_run_successful(self):
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

    def test_cake_process_from_spec_successful(self):
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

    def test_cake_process_from_run_successful(self):
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

    def test_cake_process_from_spec_and_run_successful(self):
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

    def test_cake_measurement_from_spec_successful(self):
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

    def test_cake_measurement_from_run_successful(self):
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

    def test_cake_measurement_from_spec_and_run_successful(self):
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

    ################# Ingredient #########################

    def test_cake_ingredient_from_spec_successful(self):
        cake_example = cake.make_cake(seed=42)
        ingredient_spec = cake_example.process.ingredients[0].spec
        ingredient_from_spec = from_spec_or_run(
            name=ingredient_spec.name, spec=ingredient_spec
        )
        self.assertEquals(ingredient_from_spec.name, ingredient_spec.name)
        self.assertEqual(
            ingredient_spec.uids["citrine-demo"],
            ingredient_from_spec.spec.uids["citrine-demo"],
        )

    def test_cake_ingredient_from_run_successful(self):
        cake_example = cake.make_cake(seed=42)
        ingredient_run = cake_example.process.ingredients[0]
        ingredient_from_run = from_spec_or_run(
            name=ingredient_run.name, run=ingredient_run
        )
        self.assertEquals(ingredient_from_run.name, ingredient_run.name)
        self.assertEqual(
            ingredient_run.uids["citrine-demo"],
            ingredient_from_run.run.uids["citrine-demo"],
        )

    def test_cake_ingredient_from_spec_and_run_successful(self):
        cake_example = cake.make_cake(seed=42)
        ingredient_run = cake_example.process.ingredients[0]
        ingredient_spec = ingredient_run.spec
        ingredient_from_spec_and_run = from_spec_or_run(
            name=ingredient_run.name, spec=ingredient_spec, run=ingredient_run
        )
        self.assertEquals(ingredient_from_spec_and_run.name, ingredient_run.name)
        self.assertEqual(
            ingredient_run.uids["citrine-demo"],
            ingredient_from_spec_and_run.run.uids["citrine-demo"],
        )
        self.assertEqual(
            ingredient_spec.uids["citrine-demo"],
            ingredient_from_spec_and_run.spec.uids["citrine-demo"],
        )

    ################# Block #########################
    def test_materials_data_block_from_material_successful(self):
        alloy_ingredient = Ingredient("Alloy Ingredient")
        polishing_process = Process("Polishing", template=ProcessTemplate("Heating"))
        polished_alloy = Material("Polished Alloy", template=MaterialTemplate("Alloy"))
        first_temperature_measurement = Measurement(
            "First Temperature", template=MeasurementTemplate("temperature")
        )
        second_temperature_measurement = Measurement(
            "Second Temperature", template=MeasurementTemplate("temperature")
        )
        polishing_block = ProcessBlock(
            name=f"Polishing Alloy",
            workflow=None,
            material=polished_alloy,
            ingredients=[alloy_ingredient],
            process=polishing_process,
            measurements=[
                first_temperature_measurement,
                second_temperature_measurement,
            ],
        )
        polishing_block.link_within()

        identical_block = ProcessBlock.from_spec_or_run(
            "identical_block",
            notes=None,
            spec=polishing_process.spec,
            run=polishing_process.run,
        )

        self.assertEquals(
            polishing_block.material.template.uids["auto"],
            identical_block.material.template.uids["auto"],
        )
        self.assertEquals(
            polishing_block.material.spec.uids["auto"],
            identical_block.material.spec.uids["auto"],
        )
        self.assertEquals(
            polishing_block.material.run.uids["auto"],
            identical_block.material.run.uids["auto"],
        )
        self.assertEquals(
            polishing_block.process.template.uids["auto"],
            identical_block.process.template.uids["auto"],
        )
        self.assertEquals(
            polishing_block.process.spec.uids["auto"],
            identical_block.process.spec.uids["auto"],
        )
        self.assertEquals(
            polishing_block.process.run.uids["auto"],
            identical_block.process.run.uids["auto"],
        )

        for measurement_name in polishing_block.measurements.keys():
            self.assertEquals(
                polishing_block.measurements[measurement_name].template.uids["auto"],
                identical_block.measurements[measurement_name].template.uids["auto"],
            )
            self.assertEquals(
                polishing_block.measurements[measurement_name].spec.uids["auto"],
                identical_block.measurements[measurement_name].spec.uids["auto"],
            )
            self.assertEquals(
                polishing_block.measurements[measurement_name].run.uids["auto"],
                identical_block.measurements[measurement_name].run.uids["auto"],
            )

        for ingredient_name in polishing_block.ingredients.keys():
            self.assertEquals(
                polishing_block.measurements[ingredient_name].template.uids["auto"],
                identical_block.measurements[ingredient_name].template.uids["auto"],
            )
            self.assertEquals(
                polishing_block.measurements[ingredient_name].spec.uids["auto"],
                identical_block.measurements[ingredient_name].spec.uids["auto"],
            )
            self.assertEquals(
                polishing_block.measurements[ingredient_name].run.uids["auto"],
                identical_block.measurements[ingredient_name].run.uids["auto"],
            )

    ################# Block #########################
    def test_materials_data_workflow_from_material_successful(self):
        ###
        alloy_ingredient = Ingredient("Alloy Ingredient")
        polishing_process = Process("Polishing", template=ProcessTemplate("Heating"))
        polished_alloy = Material("Polished Alloy", template=MaterialTemplate("Alloy"))
        polishing_block = ProcessBlock(
            name=f"Polishing Alloy",
            workflow=None,
            material=polished_alloy,
            ingredients=[alloy_ingredient],
            process=polishing_process,
            measurements=[],
        )
        polishing_block.link_within()

        ###
        polished_alloy_ingredient = Ingredient("Polished Alloy Ingredient")
        heating_process = Process(
            "Heating",
            template=ProcessTemplate(
                "Heating",
                parameters=ParameterTemplate(
                    name="Temperature",
                    bounds=RealBounds(0, 1500, "Kelvin"),
                ),
            ),
        )
        heated_alloy = Material("Heated Alloy", template=MaterialTemplate("Alloy"))
        heating_block = ProcessBlock(
            name=f"Heating Alloy",
            workflow=None,
            material=heated_alloy,
            ingredients=[polished_alloy_ingredient],
            process=heating_process,
            measurements=[],
        )
        heating_block.link_within()
        heating_block.link_prior(
            polishing_block, ingredient_name_to_link="Polished Alloy Ingredient"
        )

        ####
        # identical_workflow = Workflow.from_spec_or_run('identical workflow', notes=None, spec=, run=)
        pass
