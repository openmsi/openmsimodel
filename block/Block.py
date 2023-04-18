from ..workflow import Workflow
from typing import ClassVar, Type, Optional
from entity.base.material import Material
from entity.base.base_node import BaseNode

# TODO: enforce 1 process only?
class Block():
    '''
    '''
    def init(self, 
             workflow: Workflow = None,
             ingredients: Optional[list] = [],
             process: Optional[BaseNode] = None,
             material: Optional[Material] = None,
             measurements: Optional[list] = [],
             ):
        self.workflow = workflow
        self.ingredients = ingredients
        self.process = process
        self.material = material
        self.measurements = measurements
        pass

    def thin_dumps(self):
        pass
    
    def dumps(self):
        pass
    
    def link_within(self):
        # link ingredients to process
        if self.ingredients is not []:
            for i in self.ingredients:
                i._spec.process = self.process._spec
                i._run.process = self.process._run
        # link process to material
        if self.material is not None:
            self.material._spec.process = self.process._spec
            self.material._run.process = self.process._run
        # link measurements to material
        if self.measurements is not []:
            for m in self.measurements:
                m._run.material = self.material._run
    
    def link_prior(self):
        pass
    
    def link_posterior(self):
        pass
    
    def add_ingredient(self):
        pass
    
    def add_process(self):
        pass
    
    def add_material(self):
        pass
    
    def add_measurement(self):
        pass
    