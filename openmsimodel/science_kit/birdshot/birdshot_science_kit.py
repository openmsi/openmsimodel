from openmsimodel.science_kit.science_kit import ScienceKit
from openmsimodel.science_kit.folder_or_file import FolderOrFile
from openmsimodel.tools.structures.materials_sequence import MaterialsSequence
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.entity.gemd.ingredient import Ingredient

from openmsimodel.entity.gemd.processes.birdshot.summarize import (
    Summarize,
)
from openmsimodel.entity.gemd.processes.birdshot.infer_compositions import (
    InferCompositions,
)
from openmsimodel.entity.gemd.processes.birdshot.select_composition import (
    SelectComposition,
)
from openmsimodel.entity.gemd.processes.birdshot.add_material import AddMaterial
from openmsimodel.entity.gemd.processes.birdshot.mixing import Mixing
from openmsimodel.entity.gemd.processes.birdshot.arc_melting import ArcMelting
from openmsimodel.entity.gemd.processes.birdshot.homogenization import Homogenization
from openmsimodel.entity.gemd.processes.birdshot.forging import Forging
from openmsimodel.entity.gemd.processes.birdshot.setting_traveler import SettingTraveler
from openmsimodel.entity.gemd.processes.birdshot.setting_traveler_sample import (
    SettingTravelerSample,
)
from openmsimodel.entity.gemd.processes.birdshot.aggregate_traveler_samples import (
    AggregateTravelerSamples,
)


from openmsimodel.entity.gemd.materials.birdshot.summary import Summary
from openmsimodel.entity.gemd.materials.birdshot.inferred_alloy_compositions import (
    InferredAlloyCompositions,
)
from openmsimodel.entity.gemd.materials.birdshot.composition import Composition
from openmsimodel.entity.gemd.materials.birdshot.element import Element
from openmsimodel.entity.gemd.materials.birdshot.alloy import Alloy
from openmsimodel.entity.gemd.materials.birdshot.traveler import Traveler
from openmsimodel.entity.gemd.materials.birdshot.traveler_sample import TravelerSample
from openmsimodel.entity.gemd.materials.birdshot.traveler_samples import TravelerSamples

from openmsimodel.entity.gemd.measurements.birdshot.weighting import Weighting
from openmsimodel.entity.gemd.measurements.birdshot.measure_dimensions import (
    MeasureDimensions,
)
from openmsimodel.entity.gemd.measurements.birdshot.sem import SEM
from openmsimodel.entity.gemd.measurements.birdshot.ni import NI
from openmsimodel.entity.gemd.measurements.birdshot.xrd import XRD
from openmsimodel.entity.gemd.measurements.birdshot.tensile import Tensile
from openmsimodel.entity.gemd.measurements.birdshot.mounting_and_polishing import (
    MountingAndPolishing,
)
from openmsimodel.entity.gemd.measurements.birdshot.srjt import SRJT

from openmsimodel.utilities.tools import plot_graph
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from openmsimodel.science_kit.birdshot.helpers import *

import json
import os
import shutil

# import pandas as pd
from pathlib import Path
from collections import defaultdict
import time
import sys

from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
from gemd.entity.attribute import Property, Parameter, Condition, PropertyAndConditions
from gemd.entity.value import NominalReal, NominalCategorical
from gemd.entity.util import make_instance
from gemd.entity import PerformedSource, FileLink
from gemd.json import GEMDJson
from gemd.util.impl import recursive_foreach


class BIRDSHOTScienceKit(ScienceKit, FolderOrFile):
    def __init__(self, root, output, iteration, synthesis_path, srjt_path):
        """
        this function represents a TAMU science_kit, from a list of compositions to tests, through their
        VAM and DED fabrications, their splits into travelers for numerous characterizations, all the way to
        using the characterization results to infer the next compositions using BO.
        :param iteration: the iteration of the science_kit (i.e., AAB)
        :param synthesis_path: the path to synthesis file (i.e., /Sample Data/Iteration2_AAB/HTMDEC AAB Summary Synthesis Results)
        :param srjt_path: the path to srjt file
        """
        ScienceKit.__init__(self)
        # self.root gets set in FolderOrFile
        FolderOrFile.__init__(self, root, parent_path=None, is_last=False)
        self.encoder = GEMDJson()
        self.output = Path(output)
        self.iteration = iteration
        self.synthesis_path = Path(synthesis_path)
        self.srjt_path = Path(srjt_path)
        recursive_dict = lambda: defaultdict(recursive_dict)
        self.subs = recursive_dict()  # overwrite
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

    def build(self):
        # ingesting the results of the summary sheet, which is associated with each composition space, and science_kit object
        print("Building...")
        if "AAA" in str(self.synthesis_path):
            ingest_aaa_synthesis_results(
                self.iteration, self.synthesis_path, self.file_links, self.measurements
            )
        else:
            ingest_synthesis_results(
                self.iteration, self.synthesis_path, self.file_links, self.measurements
            )

        ingest_srjt_results(self.srjt_path, self.output, self.measurements)

        ############## block 1: first infer_compositions_block
        def create_infer_compositions_block():
            # collecting all the compositions in the composition space to be assigned as tags
            compositions_tags = []
            for composition_id in self.measurements.keys():
                for element_name, element_percentage in self.measurements[
                    composition_id
                ]["Target Composition, at.%"].items():
                    compositions_tags.append(
                        (
                            "{}::{}".format(composition_id, element_name),
                            str(element_percentage),
                        )
                    )

            # TODO: link this to the last node
            inferred_alloy_compositions = InferredAlloyCompositions(
                "Inferred Alloy Compositions"
            )

            inferred_alloy_compositions._set_tags(
                tags=compositions_tags,
                spec_or_run=inferred_alloy_compositions.run,
            )
            for obj in [
                inferred_alloy_compositions.run,
                inferred_alloy_compositions.spec,
            ]:
                inferred_alloy_compositions._set_filelinks(
                    spec_or_run=obj,
                    supplied_links={"Summary Sheet": self.file_links["Summary Sheet"]},
                )
            infer_compositions_block_name = "Infer Compositions"
            infer_compositions_block = MaterialsSequence(
                name=infer_compositions_block_name,
                science_kit=self,
                ingredients=[],
                process=None,
                material=inferred_alloy_compositions,
            )
            infer_compositions_block.link_within()
            self.subs[infer_compositions_block_name] = infer_compositions_block
            return infer_compositions_block, inferred_alloy_compositions

        (
            infer_compositions_block,
            inferred_alloy_compositions,
        ) = create_infer_compositions_block()
        self.initial_material = inferred_alloy_compositions.run

        self.subs[infer_compositions_block.name] = infer_compositions_block

        # extracting tree structure to build the model up
        count = 0
        path_offset = 6
        tree_folders_and_files = self.make_tree(FolderOrFile, self.root)

        tree_folders_and_files_copy = list(self.make_tree(FolderOrFile, self.root))
        with open(self.output / "folder_structure.txt", "w") as fp:
            for p in tree_folders_and_files_copy:
                fp.write(p.displayable() + "\n")

        ############## blocks from 2 to (n-3)
        # looping through all the folders and files in the tree structure
        for item in tree_folders_and_files:
            item_path = str(item.root)
            # print(item_path)
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
                if is_ded:  # FIXME
                    continue
                split_item_path = substring_after(item_path, str(self.root))
                if split_item_path[0] == "/":  # avoiding first '/'
                    split_item_path = split_item_path[1:]
                split_item_path = split_item_path.split("/")
                fabrication_method = split_item_path[
                    0
                ]  # path offset used to removes path elements before data (i.e., ../data/)
                batch = split_item_path[1]
                if is_ded:
                    if item.depth == 4:
                        continue
                    elif item.depth >= 5:
                        composition_id = split_item_path[3]
                else:
                    composition_id = split_item_path[2]
                if (item.depth == 4 and not is_ded) or (item.depth == 5 and is_ded):
                    if onlyfiles or is_ded:  # FIXME
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
                        item_path,
                        composition_id,
                        batch,
                        fabrication_method,
                    )

        # adding average tensile measurement manually
        def add_average_tensile_measurement():
            """
            assigns the average tensile measurement from the excel summary sheet to the model
            (since it is reflected only in the summary sheet, not in the tree structure as a folder/measurement or else)
            """
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

        ############## block -3: aggregation of traveler samples by category
        def extract_traveler_samples_blocks():
            traveler_samples_blocks = defaultdict(lambda: [])
            for composition_id in self.terminal_blocks.keys():
                for fabrication_method in self.terminal_blocks[composition_id].keys():
                    for batch in self.terminal_blocks[composition_id][
                        fabrication_method
                    ].keys():
                        terminal_blocks = self.terminal_blocks[composition_id][
                            fabrication_method
                        ][batch]
                        for terminal_block in terminal_blocks:
                            traveler_samples_blocks[terminal_block.type].append(
                                terminal_block
                            )
            return traveler_samples_blocks

        traveler_samples_blocks = extract_traveler_samples_blocks()

        terminal_blocks = []
        for traveler_sample_type in traveler_samples_blocks.keys():
            ings = []
            for traveler_sample_block in traveler_samples_blocks[traveler_sample_type]:
                ings.append(
                    Ingredient(f"{traveler_sample_block.material.run.name} Ing")
                )
            aggregate_traveler_samples_process = AggregateTravelerSamples(
                f"Aggregating {traveler_sample_type} samples"
            )
            traveler_samples_material = TravelerSamples(
                f" {traveler_sample_type} Traveler samples"
            )

            aggregate_traveler_samples_block = MaterialsSequence(
                name=f"Aggregating {traveler_sample_type} Traveler Samples",
                science_kit=self,
                ingredients=ings,
                process=aggregate_traveler_samples_process,
                material=traveler_samples_material,
                _type="manual",
            )
            aggregate_traveler_samples_block.link_within()
            for traveler_sample_block in traveler_samples_blocks[traveler_sample_type]:
                aggregate_traveler_samples_block.link_prior(
                    traveler_sample_block,
                    ingredient_name_to_link=f"{traveler_sample_block.material.run.name} Ing",
                )
            terminal_blocks.append(aggregate_traveler_samples_block)

        ############## block -2: aggregation of summary sheet block
        # FIXME
        aggregate_summary_process = Summarize("Summarize inputs to B.O")
        summary_material = Summary("Summary")
        summary_block = MaterialsSequence(
            name="Summary",
            science_kit=self,
            ingredients=[],
            process=aggregate_summary_process,
            material=summary_material,
            _type="manual",
        )

        def link_traveler_samples_to_summary_sheet():
            """
            this functions takes all the traveler samples build in the process_measurement() calls,
            and converts them to ingredients to the next process, which is aggregation the summary sheet block, a
            and which will ultimately be used for the Bayesian optimization process.
            """
            for terminal_block in terminal_blocks:
                ingredient_name = "{} Ing".format(terminal_block.material._run.name)
                ingredient = Ingredient(ingredient_name)
                summary_block.ingredients[ingredient.name] = ingredient
                summary_block.link_within()
                summary_block.link_prior(
                    terminal_block, ingredient_name_to_link=ingredient_name
                )
            self.subs[summary_block.name] = summary_block

        # an important step to link all the measurements on traveler samples to the summary sheet of the NEXT iteration
        link_traveler_samples_to_summary_sheet()

        ############## block -1: Bayesian Optimization block
        summary_sheet_name = summary_block.material._run.name
        summary_ingredient = Ingredient("{} Ing".format(summary_sheet_name))
        infer_compositions_process = InferCompositions("Infer comp. using B.O.")
        infer_next_compositions_block = MaterialsSequence(
            name="Infer Compositions",
            science_kit=self,
            ingredients=[summary_ingredient],
            process=infer_compositions_process,
            material=None,
            _type="manual",
        )

        infer_next_compositions_block.link_within()
        infer_next_compositions_block.link_prior(
            summary_block,
            ingredient_name_to_link=summary_ingredient._run.name,
        )
        self.subs[summary_block.name] = summary_block

        # assigning terminal material
        self.terminal_process = infer_next_compositions_block.process.run

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
                item_path_content = os.listdir(item_path)
                processing_details = list(
                    filter(lambda x: "processing-details" in x, item_path_content)
                )
                if len(processing_details) == 0:
                    processing_details = {}
                else:
                    assert len(processing_details) == 1
                    processing_details = json.load(
                        open(
                            os.path.join(
                                item_path,
                                processing_details[0],
                            )
                        )
                    )

                synthesis_details = list(
                    filter(lambda x: "synthesis-details" in x, item_path_content)
                )
                if len(synthesis_details) == 0:
                    synthesis_details = {}
                else:
                    assert len(synthesis_details) == 1
                    synthesis_details = json.load(
                        open(
                            os.path.join(
                                item_path,
                                synthesis_details[0],
                            )
                        )
                    )

                traveler = list(filter(lambda x: "traveler" in x, item_path_content))
                if len(traveler) == 0:
                    traveler = {}
                else:
                    assert len(traveler) == 1
                    traveler = json.load(
                        open(
                            os.path.join(
                                item_path,
                                traveler[0],
                            )
                        )
                    )
                yymm = traveler["data"]["Sample ID"]["Year & Month"]
                return processing_details, synthesis_details
            except:
                return {}, {}

        processing_details, synthesis_details = read_details()
        if len(processing_details) == 0 or len(synthesis_details) == 0:
            return

        (
            long_name,
            short_name,
            alloy_common_name,
            common_tags,
        ) = return_common_items(composition_id, fabrication_method, batch, yymm)

        ############## block 1: Selecting composition
        inferred_alloy_compositions_ingredient_name = "{} Ing".format(
            inferred_alloy_compositions._spec.name
        )
        inferred_alloy_compositions_ingredient = Ingredient(
            inferred_alloy_compositions_ingredient_name
        )
        select_composition_process = SelectComposition(f"Select {composition_id}")
        composition_material = Composition(f"Composition {composition_id}")

        def set_composition_material_and_select_composition_process_params_and_tags():
            composition_tags = tuple(
                [
                    (element_name, str(element_percentage))
                    for element_name, element_percentage in self.measurements[
                        composition_id
                    ]["Target Composition, at.%"].items()
                ]
            )
            composition_and_common_tags = common_tags + composition_tags
            select_composition_process._set_tags(
                tags=composition_and_common_tags,
                spec_or_run=select_composition_process.run,
            )
            composition_material._set_tags(
                tags=composition_and_common_tags,
                spec_or_run=composition_material.run,
            )
            item_path_file_link = FileLink(filename="root", url=item_path) ##########
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

        block1 = MaterialsSequence(
            name=f"Selecting Composition {composition_id}",
            science_kit=self,
            ingredients=[inferred_alloy_compositions_ingredient],
            process=select_composition_process,
            material=composition_material,
        )
        block1.link_within()
        block1.link_prior(
            prior_block,
            ingredient_name_to_link=inferred_alloy_compositions_ingredient_name,
        )
        self.subs[block1.name] = block1

        ############## block 2: Weighting + aggregating (or buying) materials (one to many)
        composition_elements = []
        parallel_block2s = []
        composition_ingredient_name = "{} Ing".format(composition_material._spec.name)
        # composition_ingredient = Ingredient(composition_ingredient_name)
        for (
            element_name,
            element_property,
        ) in composition_tags:  # TODO: if aggregate_or_buy
            composition_ingredient = Ingredient(composition_ingredient_name)

            adding_material_process = AddMaterial(
                f"Adding {element_name} for {composition_id}"
            )
            adding_material_process._set_tags(
                tags=common_tags,
                spec_or_run=adding_material_process.run,
            )
            composition_element_material = Element(
                "{} in {}".format(element_name, composition_id)
            )

            # source obj
            weighting_performed_source = None
            if synthesis_details:
                preparation_metadata = synthesis_details["data"][
                    "Material Preparation"
                ]["Process Overview"]
                weighting_performed_source = PerformedSource(
                    preparation_metadata["Completed By"],
                    preparation_metadata["Finish Date"],
                )

            target_mass = None
            weighted_mass = None

            def set_composition_element_material_params_and_tags():
                if synthesis_details:
                    target_mass = synthesis_details["data"]["Material Preparation"][
                        "Target Mass"
                    ][element_name]
                    weighted_mass = synthesis_details["data"]["Material Preparation"][
                        "Weighed Mass"
                    ][element_name]
                    composition_element_material._update_attributes(
                        AttrType=PropertyAndConditions,
                        attributes=(
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
                    ),
                )
                composition_element_material._set_tags(
                    tags=common_tags,
                    spec_or_run=composition_element_material.run,
                )
                composition_element_material._run._sample_type = "production"

            set_composition_element_material_params_and_tags()

            weighting_measurement = Weighting(
                "Weigh {} for {}".format(element_name, composition_id)
            )
            weighting_measurement._set_tags(
                tags=common_tags,
                spec_or_run=weighting_measurement.run,
            )
            if weighted_mass:
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
            block2 = MaterialsSequence(
                name="Adding {} for {}".format(element_name, short_name),
                science_kit=self,
                ingredients=[composition_ingredient],
                process=adding_material_process,
                material=composition_element_material,
                measurements=[weighting_measurement],
                _type="manual",
            )
            block2.link_within()
            block2.link_prior(
                block1, ingredient_name_to_link=composition_ingredient_name
            )
            parallel_block2s.append(block2)
            self.subs[block2.name] = block2

        ############## block 3 : mixing
        composition_element_ingredients = []
        for composition_element_material in composition_elements:
            composition_element_ingredient_name = "{} Ing".format(
                composition_element_material._run.name
            )
            composition_element_ingredient = Ingredient(
                composition_element_ingredient_name
            )
            composition_element_ingredients.append(composition_element_ingredient)
        mixing_process = Mixing(f"Mix elements of {composition_id}")
        mixing_process._set_tags(
            tags=common_tags,
            spec_or_run=mixing_process.run,
        )
        alloy_material = Alloy(alloy_common_name)
        alloy_material._set_tags(
            tags=common_tags,
            spec_or_run=alloy_material.run,
        )
        srjt_measurement = SRJT(f"SRJT charact. for {composition_id}")
        srjt_measurement._set_tags(
            tags=(("composition_id", composition_id),),
            spec_or_run=srjt_measurement.run,
        )

        for srjt_property_name in self.measurements[composition_id]["SRJT"].keys():
            attribute_value = self.measurements[composition_id]["SRJT"][
                srjt_property_name
            ]
            # if not type(value) == str:  # FIXME
            unit = srjt_measurement._ATTRS["properties"][srjt_property_name][
                "obj"
            ].bounds.default_units
            value = NominalReal(float(attribute_value), unit)
            srjt_measurement._update_attributes(
                AttrType=Property,
                attributes=(
                    Property(
                        srjt_property_name,
                        value=value,
                        origin="measured",
                        notes="",
                        file_links=[],
                    ),
                ),
                which="run",
            )

        # assigning srjt measurement to alloy at earlier phase due to measuremenet being indep. from batch/fab method

        block3 = MaterialsSequence(
            name="Mix elements of {}".format(composition_id),
            science_kit=self,
            ingredients=composition_element_ingredients,
            process=mixing_process,
            material=alloy_material,
            measurements=[srjt_measurement],
        )
        block3.link_within()
        for i, block in enumerate(parallel_block2s):
            block3.link_prior(
                block,
                ingredient_name_to_link=composition_element_ingredients[i]._run.name,
            )
        self.subs[block3.name] = block3

        ############## block 4 : fabrication
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
        ############## block 4
        arc_melting_performed_source = None
        arc_melting_metadata = None
        melted_alloy_properties = None
        if synthesis_details:
            melted_alloy_properties = synthesis_details["data"]["Arc Melting"][
                "Ingot Mass Information"
            ]

            arc_melting_metadata = synthesis_details["data"]["Arc Melting"][
                "Process Overview"
            ]
            arc_melting_performed_source = PerformedSource(
                arc_melting_metadata["Completed By"],
                arc_melting_metadata["Finish Date"],
            )

        alloy_ingredient_name = "{} Ing".format(alloy_common_name)
        alloy_ingredient = Ingredient(alloy_ingredient_name)

        arc_melting_process = ArcMelting("Arc melting of {}".format(alloy_common_name))

        def gen_arc_melting_tags():
            arc_melting_tags = ()
            for name in ["3 Part Sections", "Full Ingot"]:
                if synthesis_details:
                    _d = synthesis_details["data"]["Arc Melting"][name]
                    for key, value in _d.items():
                        tag_name = "{}::{}".format(name, key)
                        arc_melting_tags = ((tag_name, str(value)),) + arc_melting_tags
            if arc_melting_metadata:
                arc_melting_tags = (
                    ("start_date", arc_melting_metadata["Start Date"]),
                    ("finish_date", arc_melting_metadata["Finish Date"]),
                    ("time_spent", str(arc_melting_metadata["Time Spent"])),
                ) + arc_melting_tags
            return arc_melting_tags

        arc_melting_tags = gen_arc_melting_tags()
        arc_melting_and_common_tags = common_tags + arc_melting_tags
        arc_melting_process._set_tags(
            tags=arc_melting_and_common_tags,
            spec_or_run=arc_melting_process.run,
        )

        def set_arc_melting_process_params():
            if synthesis_details:
                arc_melting_parameters = synthesis_details["data"]["Arc Melting"][
                    "VAM Details"
                ]
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
            "Weigh {}".format(melted_alloy_material.name)
        )
        weighting_alloy_measurement._set_tags(
            tags=common_tags,
            spec_or_run=weighting_alloy_measurement.run,
        )
        if melted_alloy_properties:
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
                        value=NominalReal(
                            float(melted_alloy_properties["Mass Loss"]), "g"
                        ),
                    ),
                ),
                which="run",
            )
        weighting_alloy_measurement._run.source = arc_melting_performed_source

        block4 = MaterialsSequence(
            name=f"Arc Melting of Alloy {alloy_common_name}",
            science_kit=self,
            ingredients=[alloy_ingredient],
            process=arc_melting_process,
            material=melted_alloy_material,
            measurements=[weighting_alloy_measurement],
        )
        block4.link_within()
        block4.link_prior(prior_block, ingredient_name_to_link=alloy_ingredient_name)

        self.subs[block4.name] = block4

        ############## block 5
        homogenization_metadata = None
        homogenization_performed_source = None
        if processing_details:
            homogenization_metadata = processing_details["data"]["Homogenization"][
                "Process Overview"
            ]
            homogenization_performed_source = PerformedSource(
                homogenization_metadata["Completed By"],
                homogenization_metadata["Finish Date"],
            )

        melted_alloy_ingredient_name = "Arc Melted {} Ing".format(alloy_common_name)
        melted_alloy_ingredient = Ingredient(melted_alloy_ingredient_name)

        homogenization_process = Homogenization(
            "Homogenizing {}".format(alloy_common_name)
        )
        homogenization_and_common_tags = common_tags
        if homogenization_metadata:
            homogenization_tags = (
                ("start_date", homogenization_metadata["Start Date"]),
                ("finish_date", homogenization_metadata["Finish Date"]),
                ("time_spent", str(homogenization_metadata["Time Spent"])),
            )
            homogenization_and_common_tags += homogenization_tags
        homogenization_process._set_tags(
            tags=homogenization_and_common_tags,
            spec_or_run=homogenization_process.run,
        )

        def set_homogenization_process_params():
            if processing_details:
                homogenization_parameters = processing_details["data"][
                    "Homogenization"
                ]["Thermal Conditions"]
                homogenization_parameters_2 = processing_details["data"][
                    "Homogenization"
                ]["Purging Sequence Pressure"]
                for (
                    attribute_name,
                    attribute_value,
                ) in homogenization_parameters.items():
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
                for (
                    purging_step,
                    purging_pressure,
                ) in homogenization_parameters_2.items():
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
                                ]["obj"],
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
                                ]["obj"],
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

        block5 = MaterialsSequence(
            name=f"Homogenization of Alloy {alloy_common_name}",
            science_kit=self,
            ingredients=[melted_alloy_ingredient],
            process=homogenization_process,
            material=homogenized_alloy_material,
        )
        block5.link_within()
        block5.link_prior(block4, ingredient_name_to_link=melted_alloy_ingredient_name)
        self.subs[block5.name] = block5

        ############## block 6
        forging_performed_source = None
        forging_tags = None
        if processing_details:
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

        homogenized_alloy_ingredient_name = "Homogenized {} Ing".format(
            alloy_common_name
        )
        homogenized_alloy_ingredient = Ingredient(homogenized_alloy_ingredient_name)
        forging_process = Forging("Forging {}".format(alloy_common_name))
        forging_and_common_tags = common_tags
        if forging_tags:
            forging_and_common_tags += forging_tags
        forging_process._set_tags(
            tags=forging_and_common_tags,
            spec_or_run=forging_process.run,
        )

        def set_forging_process_params():
            attribute_name = "Press Temperature"
            if processing_details:
                press_temperature = processing_details["data"]["Forging"][
                    attribute_name
                ]
                value = NominalReal(press_temperature, "Kelvin")
                forging_process._update_attributes(
                    AttrType=Parameter,
                    attributes=(
                        Parameter(
                            attribute_name,
                            value=value,
                            origin="specified",
                            template=forging_process._ATTRS["parameters"][
                                "Temperature"
                            ]["obj"],
                        ),
                    ),
                    which="run",
                )
                forging_params = processing_details["data"]["Forging"][
                    "Ingot Condition"
                ]
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
                                ]["obj"],
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
            for stage in ["Before", "After"]:
                name = "Ingot Dimensions {}".format(stage)

                capture_dimensions_measurement = MeasureDimensions(name)
                capture_dimensions_measurement._set_tags(
                    tags=common_tags,
                    spec_or_run=capture_dimensions_measurement.run,
                )
                capture_dimensions_measurement._run.source = forging_performed_source
                if processing_details:
                    _dict = processing_details["data"]["Forging"][name]
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
                                    ][attribute_name]["obj"],
                                ),
                            ),
                            which="run",
                        )

        set_capture_dimensions_measurement_properties()

        block6 = MaterialsSequence(
            name=f"Forging of Alloy {alloy_common_name}",
            science_kit=self,
            ingredients=[homogenized_alloy_ingredient],
            process=forging_process,
            material=forged_alloy_material,
        )
        block6.link_within()
        block6.link_prior(
            block5, ingredient_name_to_link=homogenized_alloy_ingredient_name
        )
        self.subs[block6.name] = block6

        ############## block 7
        forged_alloy_ingredient_name = "Forged {} Ing".format(alloy_common_name)
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
        block7 = MaterialsSequence(
            name=f"Setting up of Traveler {alloy_common_name}",
            science_kit=self,
            ingredients=[forged_alloy_ingredient],
            process=setting_traveler_process,
            material=traveler_material,
        )
        block7.link_within()
        block7.link_prior(block6, ingredient_name_to_link=forged_alloy_ingredient_name)
        # print(block7)
        self.subs[block7.name] = block7
        self.terminal_blocks[composition_id][fabrication_method][batch] = block7

    def process_measurement(
        self,
        item_path,
        composition_id,
        batch,
        fabrication_method,
        bypass=False,
    ):
        """_summary_

        Args:
            item_path (_type_): _description_
            composition_id (_type_): _description_
            batch (_type_): _description_
            fabrication_method (_type_): _description_
            bypass (bool, optional): option to not add the measurement. Defaults to False.
        """
        if bypass:
            return

        not_empty = False

        # check that there is at least one file (!= folder) inside of the item folder
        measurement_file_links = {}
        if os.path.isdir(item_path):
            # for path in os.listdir(item_path):
            for root, dirs, files in os.walk(item_path):
                # if not os.path.isdir(os.path.join(item_path, path)):
                for file in files:
                    measurement_filename = file.split(".")[0]
                    measurement_file_link = FileLink(
                        filename=measurement_filename, url=os.path.join(root, file)
                    )
                    measurement_file_links[measurement_filename] = measurement_file_link
                    not_empty = True
                    break

        (
            long_name,
            short_name,
            alloy_common_name,
            common_tags,
        ) = return_common_items(composition_id, fabrication_method, batch)

        if not_empty:
            measurement_name = item_path.split("/")[-1]
            measurement_id = item_path.split("/")[-2]
            if not (measurement_name in self.measurement_types.keys()):
                return
            measurement_obj = self.measurement_types[measurement_name]
            traveler_ingredient_name = "{}: Traveler Ing".format(alloy_common_name)
            traveler_ingredient = Ingredient(traveler_ingredient_name)
            extract_sample_process = SettingTravelerSample(
                "Extract sample from {}: Traveler".format(alloy_common_name)
            )
            extract_sample_process._set_tags(
                tags=common_tags,
                spec_or_run=extract_sample_process.run,
            )
            traveler_sample = TravelerSample(
                "{}: T. Sample ({}, {})".format(
                    alloy_common_name, measurement_name, measurement_id
                )
            )
            traveler_sample._set_tags(
                tags=common_tags,
                spec_or_run=traveler_sample.run,
            )
            measurement = measurement_obj(
                "{} charact. for {} ({})".format(
                    measurement_name, alloy_common_name, measurement_id
                )
            )
            if measurement_file_links:
                measurement._set_filelinks(
                    spec_or_run=measurement.run,
                    supplied_links=measurement_file_links,
                )
            measurement_tags = (
                ("measurement_name", measurement_name),
                ("measurement_id", measurement_id),
            ) + common_tags
            measurement._set_tags(
                tags=measurement_tags,
                spec_or_run=measurement.run,
            )

            m = self.measurements[composition_id][fabrication_method][batch][
                measurement_id
            ]
            if m:
                for attribute_name, attribute_value in m.items():
                    attribute_name = attribute_name.replace("/", "_")
                    if not type(attribute_value) == str:  # FIXME
                        if (  # FIXME
                            measurement_name == "SEM"
                            and attribute_name == "Lattice Parameter"
                        ):
                            break
                        unit = measurement._ATTRS["properties"][attribute_name][
                            "obj"
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
                                origin="measured",
                                notes="",
                                file_links=[],
                            ),
                        ),
                        which="both",
                    )

            measurement_block = MaterialsSequence(
                name="Set {} T. Sample for {} ({}) charact.".format(
                    alloy_common_name, measurement_name, measurement_id
                ),
                science_kit=self,
                ingredients=[traveler_ingredient],
                process=extract_sample_process,
                material=traveler_sample,
                measurements=[measurement],
                _type=measurement_name,
            )
            measurement_block.link_within()
            measurement_block.link_prior(
                self.subs[f"Setting up of Traveler {alloy_common_name}"],
                ingredient_name_to_link=traveler_ingredient_name,
            )
            self.subs[measurement_block.name] = measurement_block

            if (
                type(self.terminal_blocks[composition_id][fabrication_method][batch])
                == list
            ):
                self.terminal_blocks[composition_id][fabrication_method][batch].append(
                    measurement_block
                )
            else:
                self.terminal_blocks[composition_id][fabrication_method][batch] = []
                self.terminal_blocks[composition_id][fabrication_method][batch].append(
                    measurement_block
                )

    ###################### HELPERS ###############

    def link_posterior(self, science_kit):
        self.terminal_process.output_material = science_kit.initial_material

    def link_prior(self, science_kit):
        self.initial_material.process = science_kit.terminal_process

    def setup_subfolder(self, composition_id, batch, fabrication_method):
        composition_id_path = os.path.join(self.output / "structured", composition_id)
        if os.path.exists(composition_id_path):
            shutil.rmtree(composition_id_path)
        os.makedirs(composition_id_path)

        fabrication_method_path = os.path.join(composition_id_path, fabrication_method)
        # if not os.path.exists(fabrication_method_path):
        os.makedirs(fabrication_method_path)

        batch_path = os.path.join(fabrication_method_path, batch)
        # if not os.path.exists(batch_path):
        os.makedirs(batch_path)

        raw_jsons_dirpath = os.path.join(batch_path, "raw_jsons")
        thin_jsons_dirpath = os.path.join(batch_path, "thin_jsons")
        os.makedirs(raw_jsons_dirpath)
        os.makedirs(thin_jsons_dirpath)

    def thin_dumps(
        self, obj, destination=None, overwrite=False
    ):  # TODO: add option to pass own target path
        self.local_out_destination = self.output / "thin"
        if destination:  # adding overwrite options
            self.local_out_destination = destination
        if overwrite:
            if os.path.exists(self.local_out_destination):
                shutil.rmtree(self.local_out_destination)
        if not os.path.exists(self.local_out_destination):
            os.makedirs(self.local_out_destination)
        else:  # notifying user that folder is not empty
            if not len(os.listdir(self.local_out_destination)) == 0:
                print("Folder is not empty.")
        print("Executing thin dumps...")
        self.dump_function = self.encoder.thin_dumps
        start = time.time()
        recursive_foreach(obj, self.out)
        end = time.time()
        print(f"Time elapsed: {end - start}")

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = [
            *superargs,
            "root",
            "output",
            "iteration",
            "synthesis_path",
            "srjt_path",
        ]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        science_kit = cls(
            args.root, args.output, args.iteration, args.synthesis_path, args.srjt_path
        )

        with open(os.path.join(args.output, "log.txt"), "w") as sys.stderr:
            science_kit.build()
            science_kit.thin_dumps(science_kit.terminal_process, overwrite=True)


def main(args=None):
    """
    Main method to run from command line
    """
    BIRDSHOTScienceKit.run_from_command_line(args)


if __name__ == "__main__":
    main()
