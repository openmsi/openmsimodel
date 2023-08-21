from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.base.material import Material, Process
from openmsimodel.entity.base.base_element import BaseElement
from .subworkflow import Subworkflow
from typing import ClassVar, Type, Optional


class ProcessBlock(Subworkflow):
    """
    ProcessBlock is a type of Subworkflow intended to represent consecutive BaseElements in the order of 'Ingredients', 'Process', 'Material', and 'Measurements'.
    It is the natural order of GEMD objects, and of our BaseElements object, which are essentially GEMD wrappers. It is a loose class and can omit some elements of the block.
    It can be a powerful way to manipulate, link, dump, etc, GEMD objects together, while Blocks themselves can be linked with one another, facilitating repeat
    elements, linking for wide (i.e., many ingredients, many measurements) or vertical (i.e., long sequence of BaseElements) workflow, etc.
    """

    def __init__(  # FIXME
        self,
        name: str,
        process: Optional[Process],
        workflow: Workflow = None,
        material: Optional[Material] = None,
        ingredients: Optional[
            dict
        ] = {},  # TODO: names have to be unique? will that be a problem?
        measurements: Optional[dict] = {},
    ):
        """initialization of ProcessBlock.

        Args:
            name (str): Block name
            process (Optional[Process]): process of block.
            workflow (Workflow, optional): workflow that block belongs to. Defaults to None.
            material (Optional[Material], optional): material of block. Defaults to None.
            ingredients (Optional[list, dict], optional): Ingredients of block. Defaults to {}.
            measurements (Optional[list,dict], optional): Ingredients of block. Defaults to {}.

        Raises:
            TypeError: 'process' argument is not set.
            TypeError: ingredients must be of type "dict".
            TypeError: measurement must be of type "dict".
        """

        Subworkflow.__init__(self, name, workflow=workflow)
        # if process is None: #FIXME
        #     raise TypeError("'process' argument is not set. ")
        # self.name = name
        self.material = material
        # FIXME
        self.ingredients = {}
        if type(ingredients) == list:
            for i in ingredients:
                self.ingredients[i.name] = i
        # if ingredients and not (type(ingredients) == dict):
        #     raise TypeError('ingredients must be of type "dict".')
        # self.ingredients = ingredients
        self.process = process
        self.measurements = {}
        if type(measurements) == list:
            for i in measurements:
                self.measurements[i.name] = i
        # if measurements and not (type(measurements) == dict):
        #     raise TypeError('measurement must be of type "dict".')
        # self.measurements = measurements

    def link_within(self):
        """this functions links the specs and runs of the BaseElements in the current block."""
        # link ingredients to process
        if self.ingredients and self.process:
            for name in self.ingredients.keys():
                self.ingredients[name].spec.process = self.process.spec
                self.ingredients[name].run.process = self.process.run
        # link process to material
        if self.material and self.process:
            self.material.spec.process = self.process.spec
            self.material.run.process = self.process.run
        # link measurements to material
        if self.measurements and self.material:
            for name in self.measurements.keys():
                self.measurements[name].run.material = self.material.run

    def link_prior(self, prior_block, ingredient_name_to_link):
        """links the prior block's material to current ingredient.

        Args:
            prior_block (Block): prior block containing the material to link
            ingredient_name_to_link (str): name of the ingredient in current block to link to prior material
        """

        for name in self.ingredients.keys():
            if self.ingredients[name].run.name == ingredient_name_to_link:
                self.ingredients[name].spec.material = prior_block.material.spec
                self.ingredients[name].run.material = prior_block.material.run

    def link_posterior(self, posterior_block, ingredient_name_to_link):
        """link the posterior block's ingredient to current material

        Args:
            posterior_block (Block): posterior block containing the ingredient to link
            ingredient_name_to_link (str): _description_
        """
        for name in posterior_block.ingredients.keys():
            if posterior_block.ingredients[name].run.name == ingredient_name_to_link:
                posterior_block.ingredients[name].spec.material = self.material.spec
                posterior_block.ingredients[name].run.material = self.material.run

    def add_ingredient(self):
        """add ingredient to block"""
        pass

    def add_process(self):
        """add process to block"""
        pass

    def add_material(self):
        """add material to block"""
        pass

    def add_measurement(self):
        """add measurement to block"""
        pass
