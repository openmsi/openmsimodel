from workflow import Workflow
from typing import ClassVar, Type, Optional
from entity.base.material import Material
from entity.base.base_node import BaseNode

class Block():
    '''
    '''
    def __init__(self, 
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
    
    def link_prior(self, prior_block, ingredient_name_to_link):
        # links the prior block's material to current ingredient
        # print(ingredient_name_to_link)
        for i, _ in enumerate(self.ingredients): 
            # print('here')
            # print(i)
            # print(self.ingredients[i]._run.name)
            if self.ingredients[i]._run.name == ingredient_name_to_link:
                # if ingredient_name_to_link == 'V Ingredient':
                #     print('V')
                #     print(ingredient_name_to_link)
                #     print(self.workflow.print_thin_encoded(prior_block.material._spec))
                #     print(self.workflow.print_thin_encoded(prior_block.material._run))
                #     print("done")
                self.ingredients[i]._spec.material = prior_block.material._spec
                self.ingredients[i]._run.material = prior_block.material._run
                # print("check")
        # links the 
    
    def link_posterior(self, posterior_block, ingredient_name_to_link):
        # link the posterior block's ingredient to current material
        for i in posterior_block.ingredients:
            if i._run.name == ingredient_name_to_link: 
                i._spec.material = self.material._spec
                i._run.material = self.material._run
    
    def add_ingredient(self):
        pass
    
    def add_process(self):
        pass
    
    def add_material(self):
        pass
    
    def add_measurement(self):
        pass
    