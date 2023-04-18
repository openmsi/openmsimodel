
from .Workflow import Workflow
from entity.base import Material, Process, Measurement, Ingredient
from block.Block import Block
import gemd
import sys

from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
from gemd.entity.attribute import Property, Parameter, Condition, PropertyAndConditions
from gemd.entity.value import NominalReal
from gemd.entity.util import make_instance
from gemd.entity import PerformedSource, FileLink
from gemd.json import GEMDJson

helpers_path = '/srv/hemi01-j01/htmdec/tamu_htmdec_new/gemd/helpers'
sys.path.append(helpers_path)
from helpers.attribute_templates import ATTR_TEMPL
from helpers.object_templates import OBJ_TEMPL
from helpers.object_specs import OBJ_SPECS

class TAMUWorkflow(Workflow):
    
    def init(self, path, parent_path, is_last=False):
        super().__init__(self, path, parent_path, is_last)
    
    
    def build_model(self):
        
        # block
        aggregate_summary_sheet_process_spec = Process()
        aggregate_summary_sheet_process_spec.from_spec_or_run(
            ProcessSpec(
            'Aggregate summary sheet',
            template=OBJ_TEMPL['Aggregating'],
            conditions=[],
            parameters=[],
            tags=[],
            file_links=[],
            notes=None
        )
        )
        summary_sheet_material_spec = Material()
        summary_sheet_material_spec.from_spec_or_run(
            MaterialSpec(
            'Summary Sheet',
            template=OBJ_TEMPL['Summary Sheet'],
            process=aggregate_summary_sheet_process_spec,
            properties=[],
            tags=[],
            file_links=[],
            notes=None
        )
        )
        block1 = Block(workflow=self, 
                       ingredients=[],
                       process=aggregate_summary_sheet_process_spec,
                       material=summary_sheet_material_spec
                       )
        block1.link_within()
        
        # block 2
        