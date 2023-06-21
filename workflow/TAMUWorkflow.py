from .Workflow import Workflow
from .folder_or_file import FolderOrFile
from block.Block import Block

from entity.base import Material, Process, Measurement, Ingredient

from entity.processes.birdshot.aggregate_summary_sheet import AggregateSummarySheet
from entity.processes.birdshot.infer_compositions import InferCompositions
from entity.processes.birdshot.select_composition import SelectComposition
from entity.processes.birdshot.aggregate_material import AggregateMaterial
from entity.processes.birdshot.mixing import Mixing
from entity.processes.birdshot.arc_melting import ArcMelting
from entity.processes.birdshot.homogenization import Homogenization
from entity.processes.birdshot.forging import Forging
from entity.processes.birdshot.setting_traveler import SettingTraveler
from entity.processes.birdshot.setting_traveler_sample import SettingTravelerSample

from entity.materials.birdshot.summary_sheet import SummarySheet
from entity.materials.birdshot.inferred_alloy_compositions import (
    InferredAlloyCompositions,
)
from entity.materials.birdshot.composition import Composition
from entity.materials.birdshot.element import Element
from entity.materials.birdshot.alloy_material import Alloy
from entity.materials.birdshot.traveler import Traveler
from entity.materials.birdshot.traveler_sample import TravelerSample

from entity.measurements.birdshot.weighting import Weighting
from entity.measurements.birdshot.measure_dimensions import MeasureDimensions
from entity.measurements.birdshot.sem import SEM
from entity.measurements.birdshot.ni import NI
from entity.measurements.birdshot.xrd import XRD
from entity.measurements.birdshot.tensile import Tensile
from entity.measurements.birdshot.mounting_and_polishing import MountingAndPolishing


from utilities.tools import plot_graph

import json
import os
import shutil
import pandas as pd
from pathlib import Path
from collections import defaultdict


from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
from gemd.entity.attribute import Property, Parameter, Condition, PropertyAndConditions
from gemd.entity.value import NominalReal, NominalCategorical
from gemd.entity.util import make_instance
from gemd.entity import PerformedSource, FileLink
from gemd.json import GEMDJson
from gemd.util.impl import recursive_foreach

# helpers folder is specific to birdshot, and found in the birdshot gemd/helpers folder
from helpers.attribute_templates import ATTR_TEMPL
from helpers.object_templates import OBJ_TEMPL
from helpers.object_specs import OBJ_SPECS


# TODO: write ingredients?
# TODO: add number/quantity attribute to SuggestedCompositions
# TODO: add ingredient attributes
# TODO: add aggregate/purchasing details
# TODO: change the _spec to _run? or not?
# TODO: add form to alloy object (melted, etc)
# TODO: figure out path offset automatically
# TODO: figure out functions for naming output files (fn)


class TAMUWorkflow(Workflow, FolderOrFile):
    def __init__(self, *args, **kwargs):
        Workflow.__init__(self, *args, **kwargs)
        FolderOrFile.__init__(self, *args)
        self.iteration = kwargs["iteration"]
        self.sample_data_folder = kwargs["sample_data_folder"]
        recursive_dict = lambda: defaultdict(recursive_dict)
        self.blocks = recursive_dict()  # overwrite
        self.terminal_blocks = recursive_dict()  # overwrite
        self.file_links = recursive_dict()
        self.measurements = recursive_dict()
        self.measurement_types = {
            "SEM": SEM,
            "XRD": XRD,
            "NI": NI,
            "Tensile": Tensile,
            "Mounting and Polishing ": MountingAndPolishing,
        }
        self.aggregate_or_buy = True
        self.testing_mode = False

    def build_model(self):
        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)

        # ingesting the results of the summary sheet on all compositions, that is associated with each composition space/workflow
        self.ingest_synthesis_results(self.iteration)

        # collecting all the compositions in the composition space to be studied to assign as tags
        compositions_tags = []
        for composition_id in self.measurements.keys():
            for element_name, element_percentage in self.measurements[composition_id][
                "Target Composition, at.%"
            ].items():
                compositions_tags.append(
                    (
                        "{}::{}".format(composition_id, element_name),
                        str(element_percentage),
                    )
                )

        # first infer_compositions_block
        inferred_alloy_compositions = InferredAlloyCompositions(
            "Inferred Alloy Compositions"
        )
        inferred_alloy_compositions._set_tags(
            tags=compositions_tags,
            spec_or_run=inferred_alloy_compositions.run,
        )
        for obj in [inferred_alloy_compositions.run, inferred_alloy_compositions.spec]:
            inferred_alloy_compositions._set_filelinks(
                spec_or_run=obj,
                supplied_links={"Summary Sheet": self.file_links["Summary Sheet"]},
            )
        infer_compositions_block_name = "Infer Compositions"
        infer_compositions_block = Block(
            name=infer_compositions_block_name,
            workflow=self,
            ingredients=[],
            process=None,
            material=inferred_alloy_compositions,
        )
        infer_compositions_block.link_within()
        self.blocks[infer_compositions_block_name] = infer_compositions_block

        # extracting tree structure to build the model up
        count = 0
        path_offset = 6
        tree_folders_and_files = self.make_tree(FolderOrFile, Path(self.root))

        for item in tree_folders_and_files:
            item_path = str(item.root)
            if os.path.isfile(item_path):
                continue
            onlyfiles = [
                f
                for f in os.listdir(item_path)
                if os.path.isfile(os.path.join(item_path, f))
            ]
            # /AAA/VAM/B/AAA01/T01 or /AAA/DED/A/AAA01-AAA08/AAA01
            if item.depth >= 4:
                is_ded = "DED" in item_path
                split_item_path = item_path.split("/")
                fabrication_method = split_item_path[
                    path_offset + 1
                ]  # path offset used to removes path elements before data (i.e., ../data/)
                batch = split_item_path[path_offset + 2]
                if is_ded:
                    if item.depth == 4:
                        continue
                    elif item.depth >= 5:
                        composition_id = split_item_path[path_offset + 4]
                else:
                    composition_id = split_item_path[path_offset + 3]
                self.blocks[composition_id][fabrication_method][batch][
                    infer_compositions_block.name
                ] = infer_compositions_block
                if (item.depth == 4 and not is_ded) or (item.depth == 5 and is_ded):
                    self.setup_subfolder(composition_id, batch, fabrication_method)
                    if onlyfiles:
                        self.process(
                            item_path,
                            composition_id,
                            batch,
                            fabrication_method,
                            inferred_alloy_compositions,
                            infer_compositions_block,
                        )
                # AAA/VAM/B/AAA01/T01/T02 or ( AAA/DED/A/AAA01-AAA08/AAA01/C01/EDS VS AAA/DED/B/AAA01-AAA08/AAA01/C01/G01 )
                if (
                    (item.depth >= 5 and not is_ded) or (item.depth >= 6 and is_ded)
                ) and (onlyfiles):
                    self.process_measurement(
                        item_path, composition_id, batch, fabrication_method
                    )

        def add_average_tensile_measurement():
            for composition_id in self.terminal_blocks.keys():
                for fabrication_method in self.terminal_blocks[composition_id].keys():
                    for batch in self.terminal_blocks[composition_id][
                        fabrication_method
                    ].keys():
                        self.process_measurement(
                            "Average/Tensile",
                            composition_id,
                            batch,
                            fabrication_method,
                            bypass=True,
                        )

        add_average_tensile_measurement()

        # block
        aggregate_summary_sheet_process = AggregateSummarySheet(
            "Aggregate summary sheet"
        )
        summary_sheet_material = SummarySheet("Summary sheet")
        aggregate_summary_sheet_block = Block(
            name="Aggregating Summary Sheet",
            workflow=self,
            ingredients=[],
            process=aggregate_summary_sheet_process,
            material=summary_sheet_material,
        )

        def link_traveler_samples_to_summary_sheet():
            for composition_id in self.terminal_blocks.keys():
                for fabrication_method in self.terminal_blocks[composition_id].keys():
                    for batch in self.terminal_blocks[composition_id][
                        fabrication_method
                    ].keys():
                        terminal_blocks = self.terminal_blocks[composition_id][
                            fabrication_method
                        ][batch]
                        for terminal_block in terminal_blocks:
                            ingredient_name = "{} Ingredient".format(
                                terminal_block.material._run.name
                            )
                            ingredient = Ingredient(ingredient_name)
                            aggregate_summary_sheet_block.ingredients.append(ingredient)
                            aggregate_summary_sheet_block.link_within()
                            aggregate_summary_sheet_block.link_prior(
                                terminal_block, ingredient_name_to_link=ingredient_name
                            )
                        self.blocks[composition_id][fabrication_method][batch][
                            aggregate_summary_sheet_block.name
                        ] = aggregate_summary_sheet_block

        link_traveler_samples_to_summary_sheet()

        # BO block
        summary_sheet_ingredient_name = aggregate_summary_sheet_block.material._run.name
        summary_sheet_ingredient = Ingredient(
            "{} Ingredient".format(summary_sheet_ingredient_name)
        )
        infer_compositions_process = InferCompositions(
            "Infer compositions using Bayesian Optimizations"
        )
        infer_next_compositions_block = Block(
            name="Infer Compositions",
            workflow=self,
            ingredients=[summary_sheet_ingredient],
            process=infer_compositions_process,
            material=None,
        )

        infer_next_compositions_block.link_within()
        infer_next_compositions_block.link_prior(
            aggregate_summary_sheet_block,
            ingredient_name_to_link=summary_sheet_ingredient._run.name,
        )

        def set_terminal_blocks():
            for composition_id in self.terminal_blocks.keys():
                for fabrication_method in self.terminal_blocks[composition_id].keys():
                    for batch in self.terminal_blocks[composition_id][
                        fabrication_method
                    ].keys():
                        self.blocks[composition_id][fabrication_method][batch][
                            infer_next_compositions_block.name
                        ] = infer_next_compositions_block
                        self.terminal_blocks[composition_id][fabrication_method][
                            batch
                        ] = infer_next_compositions_block

        set_terminal_blocks()

    def process(
        self,
        item_path,
        composition_id,
        batch,
        fabrication_method,
        inferred_alloy_compositions,
        prior_block,
    ):
        fabrication_method_lowercase = fabrication_method.lower()
        yymm = None

        def read_details():
            try:
                processing_details = json.load(
                    open(
                        os.path.join(
                            item_path,
                            "{}-processing-details-v1.json".format(
                                fabrication_method_lowercase
                            ),
                        )
                    )
                )
                synthesis_details = json.load(
                    open(
                        os.path.join(
                            item_path,
                            "{}-synthesis-details-v1.json".format(
                                fabrication_method_lowercase
                            ),
                        )
                    )
                )
                traveler = json.load(
                    open(
                        os.path.join(
                            item_path,
                            "{}-traveler-v1.json".format(fabrication_method_lowercase),
                        )
                    )
                )
                yymm = traveler["data"]["Sample ID"]["Year & Month"]

            except:
                pass
            return processing_details, synthesis_details

        processing_details, synthesis_details = read_details()

        common_name, alloy_common_name, common_tags = self.return_common_items(
            composition_id, fabrication_method, batch, yymm
        )

        # block 1: Selecting composition
        inferred_alloy_compositions_ingredient_name = "{} Ingredient".format(
            inferred_alloy_compositions._spec.name
        )
        inferred_alloy_compositions_ingredient = Ingredient(
            inferred_alloy_compositions_ingredient_name
        )
        select_composition_process = SelectComposition("Select {}".format(common_name))
        composition_material = Composition(common_name)

        def set_composition_material_and_select_composition_process_params_and_tags():
            composition_tags = tuple(
                [
                    (element_name, str(element_percentage))
                    for element_name, element_percentage in self.measurements[
                        composition_id
                    ]["Target Composition, at.%"].items()
                ]
            )
            tmp_tags = common_tags + composition_tags
            select_composition_process._set_tags(
                tags=tmp_tags,
                spec_or_run=select_composition_process.run,
            )
            composition_material._set_tags(
                tags=tmp_tags,
                spec_or_run=composition_material.run,
            )
            item_path_file_link = FileLink(filename="root", url=item_path)
            select_composition_process._set_filelinks(
                spec_or_run=select_composition_process.run,
                supplied_links={"root": item_path_file_link},
            )
            composition_material._set_filelinks(
                spec_or_run=composition_material.run,
                supplied_links={"root": item_path_file_link},
            )
            for child in os.listdir(item_path):
                child_path = os.path.join(item_path, child)
                item_path_file_link = FileLink(filename=child, url=child_path)
                select_composition_process._set_filelinks(
                    spec_or_run=select_composition_process.run,
                    supplied_links={child: item_path_file_link},
                )
                composition_material._set_filelinks(
                    spec_or_run=composition_material.run,
                    supplied_links={child: item_path_file_link},
                )

                return composition_tags

        composition_tags = (
            set_composition_material_and_select_composition_process_params_and_tags()
        )

        block1 = Block(
            name="Selecting Composition",
            workflow=self,
            ingredients=[inferred_alloy_compositions_ingredient],
            process=select_composition_process,
            material=composition_material,
        )
        block1.link_within()
        block1.link_prior(
            prior_block,
            ingredient_name_to_link=inferred_alloy_compositions_ingredient_name,
        )
        self.blocks[composition_id][fabrication_method][batch][block1.name] = block1

        # block 2: Weighting + aggregating (or buying) materials (one to many)
        composition_elements = []
        parallel_block2s = []
        composition_ingredient_name = "{} Ingredient".format(
            composition_material._spec.name
        )
        composition_ingredient = Ingredient(composition_ingredient_name)
        for element_name, element_property in composition_tags:
            # TODO: if aggregate_or_buy
            aggregating_material_process = AggregateMaterial(
                "Aggregating {}".format(common_name)
            )
            aggregating_material_process._set_tags(
                tags=common_tags,
                spec_or_run=aggregating_material_process.run,
            )
            composition_element_material = Element(
                "{} in {}".format(element_name, common_name)
            )

            preparation_metadata = synthesis_details["data"]["Material Preparation"][""]
            weighting_performed_source = PerformedSource(
                preparation_metadata["Completed By"],
                preparation_metadata["Finish Date"],
            )

            def set_composition_element_material_params_and_tags():
                target_mass = synthesis_details["data"]["Material Preparation"][
                    "Target Mass"
                ][element_name]

                composition_element_material._update_attributes(
                    AttrType=PropertyAndConditions,
                    attributes=(
                        PropertyAndConditions(
                            property=Property(
                                "Composition Percentage",
                                value=NominalReal(float(element_property), ""),
                                origin="predicted",
                                notes="",
                                file_links=[],
                            ),
                            conditions=[],
                        ),
                        PropertyAndConditions(
                            property=Property(
                                "Target Mass",
                                value=NominalReal(float(target_mass), "g"),
                                origin="computed",
                                notes="",
                                file_links=[],
                            ),
                            conditions=[],
                        ),
                    ),
                    which="spec",
                )
                composition_element_material._set_tags(
                    tags=common_tags,
                    spec_or_run=composition_element_material.run,
                )
                composition_element_material._run._sample_type = "production"

            set_composition_element_material_params_and_tags()

            weighting_measurement = Weighting(
                "Weighting {} for {}".format(element_name, common_name)
            )
            weighting_measurement._set_tags(
                tags=common_tags,
                spec_or_run=weighting_measurement.run,
            )
            weighted_mass = synthesis_details["data"]["Material Preparation"][
                "Weighed Mass"
            ][element_name]
            weighting_measurement._update_attributes(
                AttrType=Property,
                attributes=(
                    Property(
                        "Weighed Mass", value=NominalReal(float(weighted_mass), "g")
                    ),
                ),
                which="run",
            )
            weighting_measurement._run.source = weighting_performed_source

            composition_elements.append(composition_element_material)
            block2 = Block(
                name="Aggregating {} for {}".format(element_name, common_name),
                workflow=self,
                ingredients=[composition_ingredient],
                process=aggregating_material_process,
                material=composition_element_material,
                measurements=[weighting_measurement],
            )
            block2.link_within()
            block2.link_prior(
                block1, ingredient_name_to_link=composition_ingredient_name
            )
            parallel_block2s.append(block2)
            self.blocks[composition_id][fabrication_method][batch][block2.name] = block2

        # block 3 : mixing
        composition_element_ingredients = []
        for composition_element_material in composition_elements:
            composition_element_ingredient_name = "{} Ingredient".format(
                composition_element_material._run.name
            )
            composition_element_ingredient = Ingredient(
                composition_element_ingredient_name
            )
            composition_element_ingredients.append(composition_element_ingredient)
        mixing_process = Mixing("Mixing individual elements of {}".format(common_name))
        mixing_process._set_tags(
            tags=common_tags,
            spec_or_run=mixing_process.run,
        )
        alloy_material = Alloy(alloy_common_name)
        alloy_material._set_tags(
            tags=common_tags,
            spec_or_run=alloy_material.run,
        )
        block3 = Block(
            name="Mixing Elements",
            workflow=self,
            ingredients=composition_element_ingredients,
            process=mixing_process,
            material=alloy_material,
        )
        block3.link_within()
        for i, block in enumerate(parallel_block2s):
            block3.link_prior(
                block,
                ingredient_name_to_link=composition_element_ingredients[i]._run.name,
            )
        self.blocks[composition_id][fabrication_method][batch][block3.name] = block3

        # block 4 : fabrication
        if fabrication_method == "VAM":
            self.process_vam(
                composition_id,
                fabrication_method,
                batch,
                synthesis_details,
                processing_details,
                common_tags,
                alloy_common_name,
                block3,
            )

    def process_vam(
        self,
        composition_id,
        fabrication_method,
        batch,
        synthesis_details,
        processing_details,
        common_tags,
        alloy_common_name,
        prior_block,
    ):
        # block 4
        melted_alloy_properties = synthesis_details["data"]["Arc Melting"]["   "]

        arc_melting_metadata = synthesis_details["data"]["Arc Melting"][" "]
        arc_melting_performed_source = PerformedSource(
            arc_melting_metadata["Completed By"],
            arc_melting_metadata["Finish Date"],
        )

        alloy_ingredient_name = "{} Ingredient".format(alloy_common_name)
        alloy_ingredient = Ingredient(alloy_ingredient_name)

        arc_melting_process = ArcMelting("Arc melting of {}".format(alloy_common_name))

        def gen_arc_melting_tags():
            arc_melting_tags = ()
            for name in ["3 Part Sections", "Full Ingot"]:
                _d = synthesis_details["data"]["Arc Melting"][name]
                for key, value in _d.items():
                    tag_name = "{}::{}".format(name, key)
                    arc_melting_tags = ((tag_name, str(value)),) + arc_melting_tags
            arc_melting_tags = (
                ("start_date", arc_melting_metadata["Start Date"]),
                ("finish_date", arc_melting_metadata["Finish Date"]),
                ("time_spent", str(arc_melting_metadata["Time Spent"])),
            ) + arc_melting_tags
            return arc_melting_tags

        arc_melting_tags = gen_arc_melting_tags()
        tmp_tags = common_tags + arc_melting_tags
        arc_melting_process._set_tags(
            tags=tmp_tags,
            spec_or_run=arc_melting_process.run,
        )

        def set_arc_melting_process_params():
            arc_melting_parameters = synthesis_details["data"]["Arc Melting"]["  "]
            for attribute_name, attribute_value in arc_melting_parameters.items():
                if type(attribute_value) == str:
                    value = NominalCategorical(attribute_value)
                else:
                    unit = ""
                    if attribute_name == "Initial Purging Times":
                        unit = "hour"
                    value = NominalReal(attribute_value, unit)
                arc_melting_process._update_attributes(
                    AttrType=Parameter,
                    attributes=(
                        Parameter(attribute_name, value=value, origin="specified"),
                    ),
                    which="run",
                )

        set_arc_melting_process_params()
        arc_melting_process._run.source = arc_melting_performed_source

        melted_alloy_material = Alloy("Arc Melted {}".format(alloy_common_name))
        melted_alloy_material._set_tags(
            tags=common_tags,
            spec_or_run=melted_alloy_material.run,
        )
        melted_alloy_material._update_attributes(
            AttrType=PropertyAndConditions,
            attributes=(
                PropertyAndConditions(
                    property=Property(
                        "Form",
                        value=NominalCategorical("Ingot"),
                        origin="predicted",
                        notes="",
                        file_links=[],
                    ),
                    conditions=[],
                ),
            ),
            which="spec",
        )

        weighting_alloy_measurement = Weighting(
            "Weighting {}".format(melted_alloy_material)
        )
        weighting_alloy_measurement._set_tags(
            tags=common_tags,
            spec_or_run=weighting_alloy_measurement.run,
        )
        weighting_alloy_measurement._update_attributes(
            AttrType=Property,
            attributes=(
                Property(
                    "Weighed Mass",
                    value=NominalReal(
                        float(melted_alloy_properties["Final Ingot Mass"]), "g"
                    ),
                ),
                Property(
                    "Mass Loss",
                    value=NominalReal(float(melted_alloy_properties["Mass Loss"]), "g"),
                ),
            ),
            which="run",
        )
        weighting_alloy_measurement._run.source = arc_melting_performed_source

        block4 = Block(
            name="Arc Melting of Alloy",
            workflow=self,
            ingredients=[alloy_ingredient],
            process=arc_melting_process,
            material=melted_alloy_material,
            measurements=[weighting_alloy_measurement],
        )
        block4.link_within()
        block4.link_prior(prior_block, ingredient_name_to_link=alloy_ingredient_name)

        self.blocks[composition_id][fabrication_method][batch][block4.name] = block4

        # block 5
        homogenization_metadata = processing_details["data"]["Homogenization"][
            "Process Overview"
        ]
        homogenization_performed_source = PerformedSource(
            homogenization_metadata["Completed By"],
            homogenization_metadata["Finish Date"],
        )

        melted_alloy_ingredient_name = "Arc Melted {} Ingredient".format(
            alloy_common_name
        )
        melted_alloy_ingredient = Ingredient(melted_alloy_ingredient_name)

        homogenization_process = Homogenization(
            "Homogenizing {}".format(alloy_common_name)
        )
        homogenization_tags = (
            ("start_date", homogenization_metadata["Start Date"]),
            ("finish_date", homogenization_metadata["Finish Date"]),
            ("time_spent", str(homogenization_metadata["Time Spent"])),
        )
        tmp_tags = common_tags + homogenization_tags
        homogenization_process._set_tags(
            tags=tmp_tags,
            spec_or_run=homogenization_process.run,
        )

        def set_homogenization_process_params():
            homogenization_parameters = processing_details["data"]["Homogenization"][
                "Thermal Conditions"
            ]
            homogenization_parameters_2 = processing_details["data"]["Homogenization"][
                "Purging Sequence Pressure"
            ]
            for attribute_name, attribute_value in homogenization_parameters.items():
                if type(attribute_value) == str:
                    value = NominalCategorical(attribute_value)
                else:
                    unit = ""
                    if attribute_name == "Temperature":
                        unit = "Kelvin"
                    elif attribute_name == "Pressure":
                        unit = "Pa"
                    elif attribute_name == "Duration":
                        unit = "hours"
                    value = NominalReal(attribute_value, unit)
                homogenization_process._update_attributes(
                    AttrType=Parameter,
                    attributes=(
                        Parameter(attribute_name, value=value, origin="specified"),
                    ),
                    which="run",
                )
            for purging_step, purging_pressure in homogenization_parameters_2.items():
                if not purging_pressure:
                    continue
                value = NominalReal(purging_pressure, "Pa")
                homogenization_process._update_attributes(
                    AttrType=Parameter,
                    attributes=(
                        Parameter(
                            "Purging Sequence {} Pressure".format(purging_step),
                            value=value,
                            template=homogenization_process._ATTRS["parameters"][
                                "Pressure"
                            ]["param"],
                            origin="specified",
                        ),
                    ),
                    which="run",
                )
            homogenization_process._update_attributes(
                AttrType=Parameter,
                attributes=(
                    Parameter(
                        "Purging Sequence {} Pressure".format(purging_step),
                        value=value,
                        template=homogenization_process._ATTRS["parameters"][
                            "Pressure"
                        ]["param"],
                        origin="specified",
                    ),
                ),
                which="run",
            )

        set_homogenization_process_params()
        homogenization_process._run.source = homogenization_performed_source

        homogenized_alloy_material = Alloy("Homogenized {}".format(alloy_common_name))
        homogenized_alloy_material._set_tags(
            tags=common_tags,
            spec_or_run=homogenized_alloy_material.run,
        )
        homogenized_alloy_material._update_attributes(
            AttrType=PropertyAndConditions,
            attributes=(
                PropertyAndConditions(
                    property=Property(
                        "Form",
                        value=NominalCategorical("Ingot"),
                        origin="predicted",
                        notes="",
                        file_links=[],
                    ),
                    conditions=[],
                ),
            ),
            which="spec",
        )

        block5 = Block(
            name="Homogenization of Alloy",
            workflow=self,
            ingredients=[melted_alloy_ingredient],
            process=homogenization_process,
            material=homogenized_alloy_material,
        )
        block5.link_within()
        block5.link_prior(block4, ingredient_name_to_link=melted_alloy_ingredient_name)
        self.blocks[composition_id][fabrication_method][batch][block5.name] = block5

        # block 6

        forging_metadata = processing_details["data"]["Forging"]["Process Overview"]
        forging_performed_source = PerformedSource(
            forging_metadata["Completed By"],
            forging_metadata["Finish Date"],
        )
        forging_tags = (
            ("start_date", forging_metadata["Start Date"]),
            ("finish_date", forging_metadata["Finish Date"]),
            ("time_spent", str(forging_metadata["Time Spent"])),
        )

        homogenized_alloy_ingredient_name = "Homogenized {} Ingredient".format(
            alloy_common_name
        )
        homogenized_alloy_ingredient = Ingredient(homogenized_alloy_ingredient_name)
        forging_process = Forging("Forging {}".format(alloy_common_name))
        tmp_tags = common_tags + forging_tags
        forging_process._set_tags(
            tags=tmp_tags,
            spec_or_run=forging_process.run,
        )

        def set_forging_process_params():
            attribute_name = "Press Temperature"
            press_temperature = processing_details["data"]["Forging"][attribute_name]
            value = NominalReal(press_temperature, "Kelvin")
            forging_process._update_attributes(
                AttrType=Parameter,
                attributes=(
                    Parameter(
                        attribute_name,
                        value=value,
                        origin="specified",
                        template=forging_process._ATTRS["parameters"]["Temperature"][
                            "param"
                        ],
                    ),
                ),
                which="run",
            )
            forging_params = processing_details["data"]["Forging"]["Ingot Condition"]
            forging_params_2 = processing_details["data"]["Forging"]["Maximum Load"]
            for attribute_name, attribute_value in forging_params.items():
                unit = ""
                if attribute_name == "Temperature":
                    unit = "Kelvin"
                elif attribute_name == "Soak Time":
                    unit = "minutes"
                value = NominalReal(attribute_value, unit)
                forging_process._update_attributes(
                    AttrType=Parameter,
                    attributes=(
                        Parameter(attribute_name, value=value, origin="specified"),
                    ),
                    which="run",
                )

            for i, maximum_load_step_dict in enumerate(forging_params_2):
                attribute_name = next(iter(maximum_load_step_dict.keys()))
                attribute_value = next(iter(maximum_load_step_dict.values()))

                value = NominalReal(attribute_value, "Pa")
                name = "{} {}".format(attribute_name, i)
                forging_process._update_attributes(
                    AttrType=Parameter,
                    attributes=(
                        Parameter(
                            attribute_name,
                            value=value,
                            origin="specified",
                            template=forging_process._ATTRS["parameters"][
                                "Maximum Load Step"
                            ]["param"],
                        ),
                    ),
                    which="run",
                )
            forging_process._run.source = forging_performed_source

        set_forging_process_params()

        forged_alloy_material = Alloy("Forged {}".format(alloy_common_name))
        forged_alloy_material._set_tags(
            tags=common_tags,
            spec_or_run=forged_alloy_material.run,
        )

        def set_capture_dimensions_measurement_properties():
            # forged_alloy_properties = processing_details["data"]["Forging"][
            #     "Ingot Dimensions After"
            # ]
            # forged_alloy_properties_2 = processing_details["data"]["Forging"][
            #     "Ingot Dimensions Before"
            # ]
            for stage in ["Before", "After"]:
                name = "Ingot Dimensions {}".format(stage)
                _dict = processing_details["data"]["Forging"][name]
                capture_dimensions_measurement = MeasureDimensions(name)
                capture_dimensions_measurement._set_tags(
                    tags=common_tags,
                    spec_or_run=capture_dimensions_measurement.run,
                )
                capture_dimensions_measurement._run.source = forging_performed_source
                for attribute_name, attribute_value in _dict.items():
                    property_name = "{} {}".format(attribute_name, stage)
                    value = NominalReal(attribute_value, "cm")
                    capture_dimensions_measurement._update_attributes(
                        AttrType=Property,
                        attributes=(
                            Property(
                                property_name,
                                value=value,
                                origin="specified",
                                template=capture_dimensions_measurement._ATTRS[
                                    "properties"
                                ][attribute_name]["prop"],
                            ),
                        ),
                        which="run",
                    )

        set_capture_dimensions_measurement_properties()

        block6 = Block(
            name="Forging of Alloy",
            workflow=self,
            ingredients=[homogenized_alloy_ingredient],
            process=forging_process,
            material=forged_alloy_material,
        )
        block6.link_within()
        block6.link_prior(
            block5, ingredient_name_to_link=homogenized_alloy_ingredient_name
        )
        self.blocks[composition_id][fabrication_method][batch][block6.name] = block6

        # block 7
        forged_alloy_ingredient_name = "Forged {} Ingredient".format(alloy_common_name)
        forged_alloy_ingredient = Ingredient(forged_alloy_ingredient_name)
        setting_traveler_process = SettingTraveler(
            "Setting traveler for {}".format(alloy_common_name)
        )
        setting_traveler_process._set_tags(
            tags=common_tags,
            spec_or_run=setting_traveler_process.run,
        )
        traveler_material = Traveler("{}: Traveler".format(alloy_common_name))
        traveler_material._set_tags(
            tags=common_tags,
            spec_or_run=traveler_material.run,
        )
        block7 = Block(
            name="Setting up of Traveler",
            workflow=self,
            ingredients=[forged_alloy_ingredient],
            process=setting_traveler_process,
            material=traveler_material,
        )
        block7.link_within()
        block7.link_prior(block6, ingredient_name_to_link=forged_alloy_ingredient_name)
        self.blocks[composition_id][fabrication_method][batch][block7.name] = block7
        self.terminal_blocks[composition_id][fabrication_method][batch] = block7

    def process_measurement(
        self, item_path, composition_id, batch, fabrication_method, bypass=False
    ):
        not_empty = False

        # check that there is at least one file (!= folder) inside of the item folder
        if os.path.isdir(item_path):
            for p in os.listdir(item_path):
                if not os.path.isdir(os.path.join(item_path, p)):
                    not_empty = True
                    break

        if not_empty or bypass:
            measurement_name = item_path.split("/")[-1]
            measurement_id = item_path.split("/")[-2]
            measurement_obj = self.measurement_types[measurement_name]
            _, alloy_common_name, _ = self.return_common_items(
                composition_id, fabrication_method, batch
            )
            traveler_ingredient_name = "{}: Traveler Ingredient".format(
                alloy_common_name
            )
            traveler_ingredient = Ingredient(traveler_ingredient_name)
            extract_sample_process = SettingTravelerSample(
                "Extract sample from {}: Traveler".format(alloy_common_name)
            )
            traveler_sample = TravelerSample(
                "{}: Traveler Sample ({}, {})".format(
                    alloy_common_name, measurement_name, measurement_id
                )
            )
            measurement = measurement_obj(
                "{} characterization for {} ({})".format(
                    measurement_name, alloy_common_name, measurement_id
                )
            )
            m = self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ]
            if m:
                for attribute_name, attribute_value in m.items():
                    attribute_name = attribute_name.replace("/", "_")

                    if not type(attribute_value) == str:
                        unit = measurement._ATTRS["properties"][attribute_name][
                            "prop"
                        ].bounds.default_units
                        value = NominalReal(float(attribute_value), unit)
                    else:
                        value = NominalCategorical(attribute_value)
                    measurement._update_attributes(
                        AttrType=Property,
                        attributes=(
                            Property(
                                attribute_name,
                                value=value,
                                origin="predicted",
                                notes="",
                                file_links=[],
                            ),
                        ),
                        which="run",
                    )

            block = Block(
                name="Setting up of Traveler Sample for {} ({}) characterization".format(
                    measurement_name, measurement_id
                ),
                workflow=self,
                ingredients=[traveler_ingredient],
                process=extract_sample_process,
                material=traveler_sample,
                measurements=[measurement],
            )
            block.link_within()
            block.link_prior(
                self.blocks[composition_id][fabrication_method][batch][
                    "Setting up of Traveler"
                ],
                ingredient_name_to_link=traveler_ingredient_name,
            )
            self.blocks[composition_id][fabrication_method][batch][block.name] = block

            if (
                type(self.terminal_blocks[composition_id][fabrication_method][batch])
                == list
            ):
                self.terminal_blocks[composition_id][fabrication_method][batch].append(
                    block
                )
            else:
                self.terminal_blocks[composition_id][fabrication_method][batch] = []
                self.terminal_blocks[composition_id][fabrication_method][batch].append(
                    block
                )

            # print(self.terminal_blocks[composition_id][fabrication_method][batch])

    def link_prior(self, workflow):
        for composition_id in workflow.terminal_blocks.keys():
            for fabrication_method in workflow.terminal_blocks[composition_id].keys():
                for batch in workflow.terminal_blocks[composition_id][
                    fabrication_method
                ].keys():
                    terminal_block = workflow.terminal_blocks[composition_id][
                        fabrication_method
                    ][batch]
                    self.blocks[
                        "Infer Compositions"
                    ].material._spec.process = terminal_block.process._spec
                    self.blocks[
                        "Infer Compositions"
                    ].material._run.process = terminal_block.process._run
                    # terminal_block.link_posterior(workflow.blocks['Infer Compositions'], ingredient_name_to_link=)

    def return_common_items(self, composition_id, fabrication_method, batch, yymm=None):
        common_name = "composition {} with {} in batch {}".format(
            composition_id, fabrication_method, batch
        )
        alloy_common_name = "Alloy ({})".format(common_name)
        common_tags = (
            ("composition_id", composition_id),
            ("batch", batch),
            ("fabrication_method", fabrication_method),
        )
        if yymm:
            common_tags = (("yymm", yymm),) + common_tags
        return common_name, alloy_common_name, common_tags

    def setup_subfolder(self, composition_id, batch, fabrication_method):
        composition_id_path = os.path.join(self.output_folder, composition_id)
        if not os.path.exists(composition_id_path):
            os.makedirs(composition_id_path)

        fabrication_method_path = os.path.join(composition_id_path, fabrication_method)
        if not os.path.exists(fabrication_method_path):
            os.makedirs(fabrication_method_path)

        batch_path = os.path.join(fabrication_method_path, batch)
        if not os.path.exists(batch_path):
            os.makedirs(batch_path)

        raw_jsons_dirpath = os.path.join(batch_path, "raw_jsons")
        thin_jsons_dirpath = os.path.join(batch_path, "thin_jsons")
        os.makedirs(raw_jsons_dirpath)
        os.makedirs(thin_jsons_dirpath)

    def thin_dumps_single_obj(self, obj):
        self.thin_dumps_obj_dest = os.path.join(self.output_folder, obj._run.name)
        if os.path.exists(self.thin_dumps_obj_dest):
            shutil.rmtree(self.thin_dumps_obj_dest)
        os.makedirs(self.thin_dumps_obj_dest)
        for _obj in [obj._spec, obj._run]:
            recursive_foreach(_obj, self.out)
        plot_graph(self.thin_dumps_obj_dest)
        plot_graph(self.thin_dumps_obj_dest, mode="spec")

    def out(self, item):
        """
        function object to run on individual item during recursion
        :param item: json item to write its destination
        """
        fn = "_".join([item.__class__.__name__, item.name, item.uids["auto"], ".json"])
        with open(os.path.join(self.tmp_path, fn), "w") as fp:
            fp.write(self.encoder.thin_dumps(item, indent=3))

    def thin_dumps(self):
        self.dump_loop(mode="thin")

    def dumps(self):
        self.dump_loop(mode="raw")

    def dump_loop(self, mode="thin"):
        for composition_id in self.gen_compositions():
            composition_id_path = os.path.join(self.output_folder, composition_id)
            for fabrication_method in self.blocks[composition_id].keys():
                if fabrication_method == "DED":
                    continue
                fabrication_method_path = os.path.join(
                    composition_id_path, fabrication_method
                )
                for batch in self.blocks[composition_id][fabrication_method].keys():
                    _destination = os.path.join(fabrication_method_path, batch)

                    if mode == "raw":
                        folder_name = "raw_jsons"
                        destination = os.path.join(_destination, folder_name)
                        if self.terminal_blocks[composition_id][fabrication_method][
                            batch
                        ]:
                            self.terminal_blocks[composition_id][fabrication_method][
                                batch
                            ].dumps(self.encoder, destination)
                        continue
                    folder_name = "thin_jsons"
                    destination = os.path.join(_destination, folder_name)
                    t = self.terminal_blocks[composition_id][fabrication_method][batch]
                    self.encoder.thin_dumps(t.process._run)
                    self.tmp_path = destination
                    if t.process:
                        for _obj in [t.process._spec, t.process._run]:
                            recursive_foreach(_obj, self.out)

                    # for block_name, block in self.blocks[composition_id][
                    #     fabrication_method
                    # ][batch].items():
                    #     block.thin_dumps(self.encoder, destination)
                    if self.testing_mode == True:
                        return

    def thin_plots(self):
        for composition_id in self.gen_compositions():
            composition_id_path = os.path.join(self.output_folder, composition_id)
            for fabrication_method in os.listdir(composition_id_path):
                fabrication_method_path = os.path.join(
                    composition_id_path, fabrication_method
                )
                for batch in os.listdir(fabrication_method_path):
                    batch_path = os.path.join(fabrication_method_path, batch)
                    batch_path = os.path.join(batch_path, "thin_jsons")
                    plot_graph(batch_path)
            if self.testing_mode == True:
                return

    def gen_compositions(self):
        ids = []
        for id in range(1, 17):
            composition_id = "0%s" % id if id % 10 == id else "%s" % id
            composition_id = str(self.root).split("/")[-1] + composition_id
            ids.append(composition_id)
        return ids

    def gemd_json_filename(self):
        pass

    def ingest_synthesis_results(self, iteration):
        file_link_name = "HTMDEC {} Summary Synthesis Results.xlsx".format(iteration)
        file_link_path = os.path.join(self.sample_data_folder, file_link_name)
        df = pd.read_excel(file_link_path)
        self.file_links["Summary Sheet"] = FileLink(
            filename=file_link_name, url=file_link_path
        )
        new_header = df.iloc[1]
        core_df = df[2:19]
        core_df.columns = new_header
        column_names = list(core_df.columns.values)
        core_df = core_df.reset_index()
        for row_index, row in core_df.iterrows():
            if row_index == 0:
                sub_header_row = row
                continue
            name = row["Alloy"]
            split_name = name.split("_")
            composition_id = split_name[0]
            yymm = split_name[1]
            fabrication_method = split_name[2]
            batch = split_name[3]

            # target composition
            target_composition_column = column_names[1]
            for i in range(2, 8):
                element_name = sub_header_row[i]
                composition = row[i]
                self.measurements[composition_id][target_composition_column][
                    element_name
                ] = composition

            # T05: averaged measured composition and difference
            measurement_id = row[8]
            average_composition_column = column_names[8]
            composition_difference_column = column_names[14]
            for i in range(9, 15):
                element_name = sub_header_row[i]
                average_composition = row[i]
                composition_difference = row[i + 6]
                self.measurements[composition_id][fabrication_method][batch][
                    measurement_id
                ][average_composition_column][element_name] = average_composition
                self.measurements[composition_id][fabrication_method][batch][
                    measurement_id
                ][composition_difference_column][element_name] = composition_difference

            # T03: phase/lattice parameters
            measurement_id = row[21]
            phase_column = column_names[21]
            lattice_parameter_column = column_names[22]
            phase = row[22]
            lattice_parameter = row[23]

            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][phase_column] = phase
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][lattice_parameter_column] = lattice_parameter

            # T03: hardness, HV, SD, HV
            measurement_id = row[24]
            hardness_column = column_names[24]
            sd_hv_column = column_names[25]
            hardness = row[25]
            sd_hv = row[26]
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][hardness_column] = hardness
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][sd_hv_column] = sd_hv

            # T08: elastic modulus, yield strength, uts, elongtation, strain hardnening
            measurement_id = row[27]
            elastic_modulus_column = column_names[27]
            yield_stength_column = column_names[28]
            uts_column = column_names[29]
            elongation_column = column_names[30]
            strain_hardening_column = column_names[31]
            derivative_column = column_names[32]
            derivative_column = derivative_column.replace("\u03c3", "d")

            elastic_modulus = row[28]
            yield_stength = row[29]
            uts = row[30]
            elongation = row[31]
            strain_hardening = row[32]
            derivative = row[33]

            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][elastic_modulus_column] = elastic_modulus
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][yield_stength_column] = yield_stength
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][uts_column] = uts
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][elongation_column] = elongation
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][strain_hardening_column] = strain_hardening
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][derivative_column] = derivative

            # T09: elastic modulus, yield strength, uts, elongtation, strain hardnening
            measurement_id = row[34]
            elastic_modulus_column = column_names[34]
            yield_stength_column = column_names[35]
            uts_column = column_names[36]
            elongation_column = column_names[37]
            strain_hardening_column = column_names[38]
            derivative_column = column_names[39]
            derivative_column = derivative_column.replace("\u03c3", "d")

            elastic_modulus = row[35]
            yield_stength = row[36]
            uts = row[37]
            elongation = row[38]
            strain_hardening = row[39]
            derivative = row[40]

            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][elastic_modulus_column] = elastic_modulus
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][yield_stength_column] = yield_stength
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][uts_column] = uts
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][elongation_column] = elongation
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][strain_hardening_column] = strain_hardening
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][derivative_column] = derivative

            # Average: elastic modulus, yield strength, uts, elongtation, strain hardnening
            measurement_id = row[41]
            elastic_modulus_column = column_names[41]
            yield_stength_column = column_names[42]
            uts_column = column_names[43]
            elongation_column = column_names[44]
            strain_hardening_column = column_names[45]
            derivative_column = column_names[46]
            derivative_column = derivative_column.replace("\u03c3", "d")

            elastic_modulus = row[42]
            yield_stength = row[43]
            uts = row[44]
            elongation = row[45]
            strain_hardening = row[46]
            derivative = row[47]

            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][elastic_modulus_column] = elastic_modulus
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][yield_stength_column] = yield_stength
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][uts_column] = uts
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][elongation_column] = elongation
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][strain_hardening_column] = strain_hardening
            self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ][derivative_column] = derivative

        strain_rate_and_temperature_df = df[19:21]
        strain_rate_and_temperature_df.columns = new_header
