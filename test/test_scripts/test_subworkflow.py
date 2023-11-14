# imports
import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")

from data.subclassing.arcmelting import ArcMelting
from data.subclassing.weighting import Weighting
from data.subclassing.alloy import Alloy

from data.subclassing.material_example import MaterialExample
from data.subclassing.measurement_example import MeasurementExample
from data.subclassing.process_example import ProcessExample
from openmsimodel.entity.gemd.impl import assign_uuid

# from openmsimodel.stores.gemd_template_store import (
#     GEMDTemplateStore,
#     all_template_stores,
#     template_store_ids,
# )

from openmsimodel.science_kit.science_kit import ScienceKit
from openmsimodel.tools.structures.materials_sequence import MaterialsSequence

from openmsimodel.entity.gemd.gemd_element import GEMDElement
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.entity.gemd.measurement import Measurement

from gemd import (
    NominalCategorical,
    NominalReal,
    CategoricalBounds,
    RealBounds,
    ProcessRun,
    ProcessSpec,
    ProcessTemplate,
    MaterialTemplate,
    MeasurementTemplate,
    Parameter,
    ParameterTemplate,
    Property,
    PropertyTemplate,
    Condition,
    ConditionTemplate,
)
from gemd.json import GEMDJson
from gemd.entity.util import make_instance


def helper(id, w):
    ingredient = Ingredient(f"ingredient {id}")
    material = MaterialExample(f"material {id}")
    process = ProcessExample(f"process {id}")
    measurement = MeasurementExample(f"measurement {id}")
    process_block = MaterialsSequence(
        name=f"Process Block {id}",
        science_kit=w,
        material=material,
        ingredients={ingredient.name: ingredient},
        process=process,
        measurements={measurement.name: measurement},
    )
    return process_block


class TestSubworkflow(unittest.TestCase):
    """this tests functions related to the subworkflow module."""

    def test_invalid_instantiations(self):
        """testing invalid cases for block instantiation/manipulation."""
        w = ScienceKit()
        with self.assertRaises(TypeError):
            process_block = MaterialsSequence(
                name=f"Process Block {id}",
                science_kit=w,
                material="wrong type",  #
                ingredients=[],
                process=None,
                measurements=[],
            )
        with self.assertRaises(TypeError):
            process_block = MaterialsSequence(
                name=f"Process Block {id}",
                science_kit=w,
                material=MaterialExample("material"),
                ingredients=[],
                process="wrong type",  #
                measurements=[],
            )
        with self.assertRaises(TypeError):
            process_block = MaterialsSequence(
                name=f"Process Block {id}",
                science_kit=w,
                material=None,
                ingredients="wrong type",  #
                process=None,
                measurements=[],
            )
        with self.assertRaises(TypeError):
            process_block = MaterialsSequence(
                name=f"Process Block {id}",
                science_kit=w,
                material=None,
                ingredients=[],
                process=None,
                measurements="wrong type",  #
            )

        with self.assertRaises(TypeError):
            process_block = MaterialsSequence(
                name=f"Process Block {id}",
                science_kit=w,
                material=None,
                ingredients=[MaterialExample("wrong type")],  #
                process=None,
                measurements=[],
            )

        with self.assertRaises(TypeError):
            process_block = MaterialsSequence(
                name=f"Process Block {id}",
                science_kit=w,
                material=None,
                ingredients=[],
                process=None,
                measurements=[MaterialExample("wrong type")],  #
            )

        with self.assertRaises(NameError):
            process_block = MaterialsSequence(
                name=f"Process Block {id}",
                science_kit=w,
                material=None,
                ingredients=[],
                process=None,
                measurements=[
                    MeasurementExample("same name twice"),
                    MeasurementExample("same name twice"),
                ],  #
            )

        # testing {add_} helpers
        process_block_1 = helper(id=1, w=w)
        with self.assertRaises(TypeError):
            process_block_1.add_ingredient("wrong type")
        with self.assertRaises(TypeError):
            process_block_1.add_measurement("wrong type")
        with self.assertRaises(TypeError):
            process_block_1.add_process("wrong type")
        with self.assertRaises(TypeError):
            process_block_1.add_material("wrong type")

        with self.assertRaises(NameError):
            process_block_1.add_ingredient(Ingredient(f"ingredient 1"))
        with self.assertRaises(NameError):
            process_block_1.add_measurement(MeasurementExample(f"measurement 1"))

    def test_process_block_instantiations(self):
        """this tests basic instantiations of ProcessBlocks and use of link_within / prior / posterior"""

        w = ScienceKit()

        process_block_1 = helper(1, w)
        process_block_1.link_within()
        self.assertEqual(  # ingredient to process
            process_block_1.ingredients["ingredient 1"].spec.process.uids["auto"],
            process_block_1.process.spec.uids["auto"],
        )
        self.assertEqual(
            process_block_1.ingredients["ingredient 1"].run.process.uids["auto"],
            process_block_1.process.run.uids["auto"],
        )  # process to material
        self.assertEqual(
            process_block_1.process.spec.output_material.uids["auto"],
            process_block_1.material.spec.uids["auto"],
        )
        self.assertEqual(
            process_block_1.process.run.output_material.uids["auto"],
            process_block_1.material.run.uids["auto"],
        )
        # material to measurement
        self.assertEqual(
            process_block_1.measurements["measurement 1"].run.material.uids["auto"],
            process_block_1.material.run.uids["auto"],
        )

        ###### # prior material to curr ingredient
        process_block_2 = helper(2, w)
        process_block_2.link_prior(
            process_block_1, ingredient_name_to_link="ingredient 2"
        )

        self.assertEqual(
            process_block_2.ingredients["ingredient 2"].spec.material.uids["auto"],
            process_block_1.material.spec.uids["auto"],
        )

        ###### curr ingredient to posterior material
        process_block_0 = helper(0, w)
        process_block_0.link_posterior(
            process_block_1, ingredient_name_to_link="ingredient 1"
        )

        self.assertEqual(
            process_block_1.ingredients["ingredient 1"].run.material.uids["auto"],
            process_block_0.material.run.uids["auto"],
        )

    # def test_block_instantiation_2(self):
    #     alloy_common_name = "A1"
    #     alloy_ingredient_name = "{} Ingredient".format(alloy_common_name)
    #     alloy_ingredient = Ingredient(alloy_ingredient_name)

    #     arc_melting_process = ArcMelting("Arc melting of {}".format(alloy_common_name))

    #     def gen_arc_melting_tags():
    #         arc_melting_tags = ()
    #         for name in ["3 Part Sections", "Full Ingot"]:
    #             _d = synthesis_details["data"]["Arc Melting"][name]
    #             for key, value in _d.items():
    #                 tag_name = "{}::{}".format(name, key)
    #                 arc_melting_tags = ((tag_name, str(value)),) + arc_melting_tags
    #         arc_melting_tags = (
    #             ("start_date", arc_melting_metadata["Start Date"]),
    #             ("finish_date", arc_melting_metadata["Finish Date"]),
    #             ("time_spent", str(arc_melting_metadata["Time Spent"])),
    #         ) + arc_melting_tags
    #         return arc_melting_tags

    #     arc_melting_tags = gen_arc_melting_tags()
    #     tmp_tags = common_tags + arc_melting_tags
    #     arc_melting_process._set_tags(
    #         tags=tmp_tags,
    #         spec_or_run=arc_melting_process.run,
    #     )

    #     def set_arc_melting_process_params():
    #         arc_melting_parameters = synthesis_details["data"]["Arc Melting"]["  "]
    #         for attribute_name, attribute_value in arc_melting_parameters.items():
    #             if type(attribute_value) == str:
    #                 value = NominalCategorical(attribute_value)
    #             else:
    #                 unit = ""
    #                 if attribute_name == "Initial Purging Times":
    #                     unit = "hour"
    #                 value = NominalReal(attribute_value, unit)
    #             arc_melting_process._update_attributes(
    #                 AttrType=Parameter,
    #                 attributes=(
    #                     Parameter(attribute_name, value=value, origin="specified"),
    #                 ),
    #                 which="run",
    #             )

    #     set_arc_melting_process_params()
    #     arc_melting_process._run.source = arc_melting_performed_source

    #     melted_alloy_material = Alloy("Arc Melted {}".format(alloy_common_name))
    #     melted_alloy_material._set_tags(
    #         tags=common_tags,
    #         spec_or_run=melted_alloy_material.run,
    #     )
    #     melted_alloy_material._update_attributes(
    #         AttrType=PropertyAndConditions,
    #         attributes=(
    #             PropertyAndConditions(
    #                 property=Property(
    #                     "Form",
    #                     value=NominalCategorical("Ingot"),
    #                     origin="predicted",
    #                     notes="",
    #                     file_links=[],
    #                 ),
    #                 conditions=[],
    #             ),
    #         ),
    #         which="spec",
    #     )

    #     weighting_alloy_measurement = Weighting(
    #         "Weighting {}".format(melted_alloy_material)
    #     )
    #     weighting_alloy_measurement._set_tags(
    #         tags=common_tags,
    #         spec_or_run=weighting_alloy_measurement.run,
    #     )
    #     weighting_alloy_measurement._update_attributes(
    #         AttrType=Property,
    #         attributes=(
    #             Property(
    #                 "Weighed Mass",
    #                 value=NominalReal(
    #                     float(melted_alloy_properties["Final Ingot Mass"]), "g"
    #                 ),
    #             ),
    #             Property(
    #                 "Mass Loss",
    #                 value=NominalReal(float(melted_alloy_properties["Mass Loss"]), "g"),
    #             ),
    #         ),
    #         which="run",
    #     )
    #     weighting_alloy_measurement._run.source = arc_melting_performed_source

    #     block4 = Block(
    #         name="Arc Melting of Alloy",
    #         science_kit=self,
    #         ingredients=[alloy_ingredient],
    #         process=arc_melting_process,
    #         material=melted_alloy_material,
    #         measurements=[weighting_alloy_measurement],
    #     )
