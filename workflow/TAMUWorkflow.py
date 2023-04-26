
from .Workflow import Workflow
from .Workflow import Folder
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
from entity.materials.birdshot.inferred_alloy_compositions import InferredAlloyCompositions
from entity.materials.birdshot.composition import Composition
from entity.materials.birdshot.composition_element import CompositionElement
from entity.materials.birdshot.alloy_material import Alloy
from entity.materials.birdshot.traveler import Traveler
from entity.materials.birdshot.traveler_sample import TravelerSample

from entity.measurements.birdshot.weighting import Weighting
from entity.measurements.birdshot.sem import SEM
from entity.measurements.birdshot.ni import NI
from entity.measurements.birdshot.xrd import XRD
from entity.measurements.birdshot.tensile import Tensile

from entity.ingredients.birdshot.summary_sheet_ingredient import SummarySheetIngredient # Not being used
from utilities.tools import plot_graph

import gemd
import sys
import json
import os
import shutil
from pathlib import Path
from collections import defaultdict

from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
from gemd.entity.attribute import Property, Parameter, Condition, PropertyAndConditions
from gemd.entity.value import NominalReal
from gemd.entity.util import make_instance
from gemd.entity import PerformedSource, FileLink
from gemd.json import GEMDJson
from gemd.util.impl import recursive_foreach

# helpers folder is specific to birdshot, and found in the birdshot gemd/helpers folder
from helpers.attribute_templates import ATTR_TEMPL
from helpers.object_templates import OBJ_TEMPL
from helpers.object_specs import OBJ_SPECS


#TODO: write ingredients?
#TODO: add number/quantity attribute to SuggestedCompositions
#TODO: change to pass iteration to build_model?
#TODO: move select composition in build_model?
#TODO: add ingredient attributes
#TODO: add aggregate/purchasing details
#TODO: tags for runs vs specs
#TODO: append the blocks
#TODO: change the _spec to _run? or not?
#TODO: add form to alloy object (melted, etc)
#TODO: figure out path offset automatically
#TODO: figure out functions for naming output files (fn)

class TAMUWorkflow(Workflow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocks = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {}))) # overwrite
        self.terminal_materials = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {}))) # overwrite
        self.measurement_types = {
            'SEM': SEM,
            'XRD': XRD,
            'NI': NI,
            'Tensile': Tensile,
        }
        
    
    def build_model(self):
        
        # block 1
        aggregate_summary_sheet_process = AggregateSummarySheet('Aggregate summary sheet')
        summary_sheet_material = SummarySheet('Summary sheet')
        block1 = Block(name='Aggregating Summary Sheet',
                       workflow=self, 
                       ingredients=[],
                       process=aggregate_summary_sheet_process,
                       material=summary_sheet_material
                       )
        block1.link_within()
        
        # block 2
        summary_sheet_ingredient_name = 'Summary sheet Ingredient'
        summary_sheet_ingredient = Ingredient(summary_sheet_ingredient_name)
        infer_compositions_process = InferCompositions('Infer compositions using Bayesian Optimizations')
        inferred_alloy_compositions = InferredAlloyCompositions('Inferred Alloy Compositions')
        block2 = Block(name='Infer Compositions',
                       workflow=self, 
                       ingredients=[summary_sheet_ingredient],
                       process=infer_compositions_process,
                       material=inferred_alloy_compositions
                       )
        block2.link_within()
        block2.link_prior(block1, ingredient_name_to_link=summary_sheet_ingredient_name)
        
        count = 0
        aggregate_or_buy = True #TODO: move to init
        path_offset = 5
        vam_identifier = 'VAM'
        ded_identifier = 'DED'
        
        tree_folders_and_files = self.make_tree(Path(self.root))
        for item in tree_folders_and_files:
            item_path = str(item.root)
            
            # if ded_identifier in item_path:
            #     if item.depth >= 5: # example: /data/AAA/DED/A/AAA01-AAA08/AAA01
            # init vars
            #         self.process_ded_batch_sample(item_path, composition_id, batch_id, inferred_alloy_compositions, block2, aggregate_or_buy)
            
            if vam_identifier in item_path:
                if item.depth >= 4: # /data/AAA/VAM/B/AAA01
                    composition_id = item_path.split('/')[path_offset+4]
                    batch_id = item_path.split('/')[path_offset+3]
                    self.blocks[composition_id][batch_id][vam_identifier][block1.name] = block1
                    self.blocks[composition_id][batch_id][vam_identifier][block2.name] = block2
                    if item.depth == 4: # example: /data/AAA/VAM/B/AAA01
                        self.process_vam_batch_sample(item_path, composition_id, batch_id, inferred_alloy_compositions, block2, aggregate_or_buy, vam_identifier)
                    if item.depth >= 6: # example: /data/AAA/VAM/B/AAA01/T01/T02, ...
                        self.process_measurement(item, item_path, composition_id, batch_id, vam_identifier)
                        
        # print(self.blocks.keys())
        # print(self.blocks['AAA01'].keys())
        # print(self.blocks['AAA01']['VAM'].keys())
        # print(self.blocks['AAA05']['VAM'].keys())
        # print(self.blocks['AAA012']['VAM'].keys())
        # print(self.blocks['AAA015']['VAM'].keys())
        
    def process_measurement(self, item, item_path, composition_id, batch_id, fabrication_method):
        
        not_empty = False
        # check that there is at least one file (!= folder) inside of the item folder
        if os.path.isdir(item_path):
            for p in os.listdir(item_path):
                if not os.path.isdir(os.path.join(item_path, p)):
                    not_empty = True
                    break

        if not_empty:
            offset = item.depth - 5
            measurement_name = item_path.split('/')[-1]
            measurement_id = item_path.split('/')[-2]
            measurement_obj = self.measurement_types[measurement_name]
            traveler_ingredient_name = '{} Alloy (Batch {}): Traveler Ingredient'.format(composition_id, batch_id)
            traveler_ingredient = Ingredient(traveler_ingredient_name)
            extract_sample_process = SettingTravelerSample('Extract sample from {} Alloy (Batch {}): Traveler'.format(composition_id, batch_id))
            traveler_sample = TravelerSample('{} Alloy (Batch {}): {} ({}) Traveler Sample'.format(composition_id, batch_id, measurement_name, measurement_id))
            measurement = measurement_obj('{} characterization'.format(measurement_name))
            
            block = Block(name='Setting up of Traveler Sample for {} ({}) characterization'.format(measurement_name, measurement_id),
                workflow=self, 
                ingredients=[traveler_ingredient],
                process=extract_sample_process,
                material=traveler_sample,
                measurements=[measurement]
            )
            block.link_within()
            block.link_prior(self.blocks[composition_id][batch_id][fabrication_method]['Setting up of Traveler'], ingredient_name_to_link=traveler_ingredient_name)
            self.blocks[composition_id][batch_id][fabrication_method][block.name] = block
            
            # self.terminal_materials[composition_id] = traveler_sample
            self.terminal_materials[composition_id][batch_id][fabrication_method] = traveler_sample
    
    def process_vam_batch_sample(self, item_path, composition_id, batch_id, inferred_alloy_compositions, prior_block, aggregate_or_buy, fabrication_method):
            
            blocks = []
            vam_processing_details = json.load(open(os.path.join(item_path, 'vam-processing-details-v1.json')))
            vam_synthesis_details = json.load(open(os.path.join(item_path, 'vam-synthesis-details-v1.json')))
            vam_traveler = json.load(open(os.path.join(item_path, 'vam-traveler-v1.json')))
            
            # composition_space_id = item_path.split('/')[1]
            # composition_id = item_path.split('/')[4]
            # batch_id = item_path.split('/')[3]
            
            self.setup_folder(composition_id, batch_id)
            
            mat_composition = vam_traveler['data']['Material Composition']
            yymm = vam_traveler['data']['Sample ID']['Year & Month']
            
            # block 1: Selecting composition
            inferred_alloy_compositions_ingredient_name = '{} Ingredient'.format(inferred_alloy_compositions._spec.name)
            inferred_alloy_compositions_ingredient = Ingredient(inferred_alloy_compositions_ingredient_name)
            select_composition_process = SelectComposition('Select composition {} in batch {}'.format(composition_id, batch_id))
            select_composition_process._set_tags(tags=[composition_id, yymm, batch_id],
                                                 spec_or_run=select_composition_process.run,
                                                 replace_all=True)
            composition_material = Composition('composition {} in batch {}'.format(composition_id, batch_id))
            composition_material._set_tags(tags=[composition_id, yymm, batch_id],
                                                 spec_or_run=composition_material.run,
                                                 replace_all=True)
            composition_material._update_attributes(
                attributes=(
                    PropertyAndConditions(property=Property('Al', value=NominalReal(float(mat_composition['Al']),'')), conditions = []),
                    PropertyAndConditions(property=Property('Co', value=NominalReal(float(mat_composition['Co']),'')), conditions = []),
                    PropertyAndConditions(property=Property('Cr', value=NominalReal(float(mat_composition['Cr']),'')), conditions = []),
                    PropertyAndConditions(property=Property('Fe', value=NominalReal(float(mat_composition['Fe']),'')), conditions = []),
                    PropertyAndConditions(property=Property('Ni', value=NominalReal(float(mat_composition['Ni']),'')), conditions = []),
                    PropertyAndConditions(property=Property('V', value=NominalReal(float(mat_composition['V']),'')), conditions = [])
                ),
                which='spec',
                AttrType=PropertyAndConditions,
                replace_all=True
            )
            block1 = Block(name="Selecting Composition",
                workflow=self, 
                ingredients=[inferred_alloy_compositions_ingredient],
                process=select_composition_process,
                material=composition_material
            )
            block1.link_within()
            block1.link_prior(prior_block, ingredient_name_to_link=inferred_alloy_compositions_ingredient_name)
            self.blocks[composition_id][batch_id][fabrication_method][block1.name] = block1
            
            # block 2: Weighting + aggregating (or buying) materials 
            composition_elements = []
            parallel_block2s = []
            composition_ingredient_name = '{} Ingredient'.format(composition_material._spec.name)
            composition_ingredient = Ingredient(composition_ingredient_name)
            for element_name, element_property in composition_material._ATTRS['properties'].items():
                #TODO: if aggregate_or_buy
                aggregating_material_process = AggregateMaterial('Aggregating composition {} in batch {}'.format(composition_id, batch_id))
                aggregating_material_process._set_tags(tags=[composition_id, yymm, batch_id],
                                                 spec_or_run=aggregating_material_process.run,
                                                 replace_all=True)
                composition_element_material = CompositionElement(element_name)
                composition_elements.append(composition_element_material)
                weighting_measurement = Weighting('Weighting {}'.format(element_name))
                
                block2 = Block(
                    name='Aggregating {}'.format(element_name),
                    workflow=self,
                    ingredients=[composition_ingredient],
                    process=aggregating_material_process,
                    material=composition_element_material,
                    measurements=[weighting_measurement]
                )
                block2.link_within()
                block2.link_prior(block1, ingredient_name_to_link=composition_ingredient_name)
                parallel_block2s.append(block2)
                self.blocks[composition_id][batch_id][fabrication_method][block2.name] = block2
                
            # block 3 
            composition_element_ingredients = []
            for composition_element_material in composition_elements:
                composition_element_ingredient_name = "{} Ingredient".format(composition_element_material._run.name)
                composition_element_ingredient = Ingredient(composition_element_ingredient_name)
                composition_element_ingredients.append(composition_element_ingredient)
            mixing_process = Mixing('Mixing individual elements of composition {} in batch {}'.format(composition_id, batch_id))
            alloy_material = Alloy('{} Alloy (Batch {})'.format(composition_id, batch_id))
            block3 = Block(name="Mixing Elements",
                           workflow=self,
                           ingredients=composition_element_ingredients,
                           process=mixing_process,
                           material=alloy_material
                           )
            block3.link_within()
            for i, block in enumerate(parallel_block2s):
                block3.link_prior(block, ingredient_name_to_link=composition_element_ingredients[i]._run.name) 
            # blocks.append(block3)
            self.blocks[composition_id][batch_id][fabrication_method][block3.name] = block3
            
            
            # block 4
            alloy_ingredient_name = '{} Alloy (Batch {}) Ingredient'.format(composition_id, batch_id)
            alloy_ingredient = Ingredient(alloy_ingredient_name)
            arc_melting_process = ArcMelting('Arc melting of composition {} in batch {}'.format(composition_id, batch_id))
            melted_alloy_material = Alloy('Arc Melted {} Alloy (Batch {})'.format(composition_id, batch_id))
            block4 = Block(name='Arc Melting of Alloy',
                           workflow=self,
                           ingredients=[alloy_ingredient],
                           process=arc_melting_process,
                           material=melted_alloy_material
                           )
            block4.link_within()
            block4.link_prior(block3, ingredient_name_to_link=alloy_ingredient_name) 
            # blocks.append(block4)
            self.blocks[composition_id][batch_id][fabrication_method][block4.name] = block4
            
            # block 5
            melted_alloy_ingredient_name = 'Arc Melted {} Alloy (Batch {}) Ingredient'.format(composition_id, batch_id)
            melted_alloy_ingredient = Ingredient(melted_alloy_ingredient_name)
            homogenization_process = Homogenization('Homogenizing composition {} in batch {}'.format(composition_id, batch_id))
            homogenized_alloy_material = Alloy('Homogenized {} Alloy (Batch {})'.format(composition_id, batch_id))
            block5 = Block(name='Homogenization of Alloy',
                           workflow=self,
                           ingredients=[melted_alloy_ingredient],
                           process=homogenization_process,
                           material=homogenized_alloy_material
                           )
            block5.link_within()
            block5.link_prior(block4, ingredient_name_to_link=melted_alloy_ingredient_name) 
            # blocks.append(block5)
            self.blocks[composition_id][batch_id][fabrication_method][block5.name] = block5
            
            
            # block 6
            homogenized_alloy_ingredient_name = 'Homogenized {} Alloy (Batch {}) Ingredient'.format(composition_id, batch_id)
            homogenized_alloy_ingredient = Ingredient(homogenized_alloy_ingredient_name)
            forging_process = Forging('Forging composition {} in batch {}'.format(composition_id, batch_id))
            forged_alloy_material = Alloy('Forged {} Alloy (Batch {})'.format(composition_id, batch_id))
            block6 = Block(name='Forging of Alloy',
                           workflow=self,
                           ingredients=[homogenized_alloy_ingredient],
                           process=forging_process,
                           material=forged_alloy_material
                           )
            block6.link_within()
            block6.link_prior(block5, ingredient_name_to_link=homogenized_alloy_ingredient_name) 
            # blocks.append(block6)
            self.blocks[composition_id][batch_id][fabrication_method][block6.name] = block6
            
            
            #block 7
            forged_alloy_ingredient_name = 'Forged {} Alloy (Batch {}) Ingredient'.format(composition_id, batch_id)
            forged_alloy_ingredient = Ingredient(forged_alloy_ingredient_name)
            setting_traveler_process = SettingTraveler('Setting traveler for composition {} in batch {}'.format(composition_id, batch_id))
            traveler_material = Traveler('{} Alloy (Batch {}): Traveler'.format(composition_id, batch_id))
            block7 = Block(name='Setting up of Traveler',
                           workflow=self,
                           ingredients=[forged_alloy_ingredient],
                           process=setting_traveler_process,
                           material=traveler_material
                           )
            block7.link_within()
            block7.link_prior(block6, ingredient_name_to_link=forged_alloy_ingredient_name) 
            # blocks.append(block7)
            self.blocks[composition_id][batch_id][fabrication_method][block7.name] = block7
            
            
            # self.blocks[composition_id]['VAM'] = blocks
            self.terminal_materials[composition_id][batch_id][fabrication_method] = traveler_material
            
    def process_ded_batch_sample(self, item_path,  inferred_alloy_compositions, prior_block, aggregate_or_buy):
        pass
    
    def setup_folder(self, composition_id, batch_id):
        composition_id_path = os.path.join(self.output_folder, composition_id)
        if os.path.exists(composition_id_path):
            shutil.rmtree(composition_id_path)
        os.makedirs(composition_id_path)
        
        batch_id_path = os.path.join(composition_id_path, batch_id)
        raw_jsons_dirpath = os.path.join(batch_id_path,'raw_jsons')
        thin_jsons_dirpath = os.path.join(batch_id_path,'thin_jsons')
        os.makedirs(raw_jsons_dirpath)
        os.makedirs(thin_jsons_dirpath)
    
    def thin_dumps_obj(self, obj):
        self.thin_dumps_obj_dest = os.path.join(self.output_folder, obj._run.name)
        if os.path.exists(self.thin_dumps_obj_dest):
            shutil.rmtree(self.thin_dumps_obj_dest)
        os.makedirs(self.thin_dumps_obj_dest)
        for _obj in [obj._spec, obj._run]:
            recursive_foreach(_obj, self.out)
        plot_graph(self.thin_dumps_obj_dest)
        plot_graph(self.thin_dumps_obj_dest, mode='spec')
        # recursive_foreach(obj, obj.thin_dumps)
    
    def out(self, item):
        '''
        function object to run on individual item during recursion 
        :param item: json item to write its destination 
        '''
        fn = '_'.join([item.__class__.__name__, item.name, item.uids['auto']])
        with open(os.path.join(self.thin_dumps_obj_dest, fn),'w') as fp :
            fp.write(self.encoder.thin_dumps(item,indent=3))
            
    def thin_dumps(self):
        for composition_id in self.gen_compositions():
            composition_id_path = os.path.join(self.output_folder, composition_id)
            for batch_id in self.blocks[composition_id].keys(): 
                destination = os.path.join(composition_id_path, batch_id)
                destination = os.path.join(destination, 'thin_jsons')
                for fabrication_method in self.blocks[composition_id][batch_id].keys():
                    for block_name, block in self.blocks[composition_id][batch_id][fabrication_method].items(): 
                        block.thin_dumps(self.encoder, destination)

    def thin_plots(self):
        for composition_id in self.gen_compositions():
            composition_id_path = os.path.join(self.output_folder, composition_id)
            for batch_id in os.listdir(composition_id_path):
                batch_id_path = os.path.join(composition_id_path, batch_id)
                batch_id_path = os.path.join(batch_id_path, 'thin_jsons')
                plot_graph(batch_id_path)
    
    def gen_compositions(self):
        ids = []
        for id in range(1,17):
            composition_id = '0%s' % id if id%10==id else '%s' % id
            composition_id = str(self.root).split('/')[-1] + composition_id
            ids.append(composition_id)
        return ids
        
        
    def gemd_json_filename(self):
        pass
    
    