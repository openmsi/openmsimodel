from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.base import Ingredient, Measurement, Material, Process
from openmsimodel.entity.base.base_element import BaseElement
from openmsimodel.subworkflow.subworkflow import Subworkflow
from typing import ClassVar, Type, Optional
from pydantic import BaseModel

# from pydantic import BaseModel as PydanticBaseModel
# class BaseModel(PydanticBaseModel):
#     class Config:
#         arbitrary_types_allowed = True


class ProcessBlock(Subworkflow, BaseModel):
    """
    ProcessBlock is a type of Subworkflow intended to represent consecutive BaseElements in the order of 'Ingredients', 'Process', 'Material', and 'Measurements'.
    It is the natural order of GEMD objects, and of our BaseElements object, which are essentially GEMD wrappers. It is a loose class and can omit some elements of the block.
    It can be a powerful way to manipulate, link, dump, etc, GEMD objects together, while Blocks themselves can be linked with one another, facilitating repeat
    elements, linking for wide (i.e., many ingredients, many measurements) or vertical (i.e., long sequence of BaseElements) workflow, etc.
    """

    name: str
    process: Optional[Process]
    workflow: Workflow = None
    material: Optional[Material] = None
    ingredients: Optional[
        dict
    ]  # TODO: names have to be unique? will that be a problem?
    measurements: Optional[dict]

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
    ):  # FIXME
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
        # BaseModel.__init__(
        #     self, name, process, workflow, material, ingredients, measurements
        # )
        BaseModel.__init__(self, **{"name": name})
        Subworkflow.__init__(self, name, workflow=workflow)
        # if process is None: #FIXME
        #     raise TypeError("'process' argument is not set. ")
        if (material and (not isinstance(material, Material))) or (
            process and not isinstance(process, Process)
        ):
            raise TypeError(
                f"Expected Material and Process; got '{type(material)}' and '{type(process)}' "
            )
        self.material = material
        self.process = process
        if type(ingredients) == dict:
            self.ingredients = ingredients
        elif type(ingredients) == list:
            self.ingredients = {}
            for i in ingredients:
                if not isinstance(i, Ingredient):
                    raise TypeError(f"Expected 'Ingredient'; got {type(i)}")
                if i.name in self.ingredients.keys():
                    raise NameError(
                        f"ingredients must have unique names. Found a duplicate: {i.name}"
                    )
                self.ingredients[i.name] = i
        else:
            raise TypeError(
                f"Expected ingredients to be a list or dict; got {type(ingredients)}"
            )

        if type(measurements) == dict:
            self.measurements = measurements
        elif type(measurements) == list:
            self.measurements = {}
            for m in measurements:
                if not isinstance(m, Measurement):
                    raise TypeError(f"Expected 'Measurement'; got {type(m)}")
                if m.name in self.measurements.keys():
                    raise NameError(
                        f"measurements must have unique names. Found a duplicate: {m.name}"
                    )
                self.measurements[m.name] = m
        else:
            raise TypeError(
                f"Expected measurements to be a list or dict; got {type(measurements)}"
            )

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

    def link_prior(self, prior_block: "ProcessBlock", ingredient_name_to_link: str):
        """links the prior block's material to current ingredient.

        Args:
            prior_block (Block): prior block containing the material to link
            ingredient_name_to_link (str): name of the ingredient in current block to link to prior material
        """

        for name in self.ingredients.keys():
            if self.ingredients[name].run.name == ingredient_name_to_link:
                self.ingredients[name].spec.material = prior_block.material.spec
                self.ingredients[name].run.material = prior_block.material.run

    def link_posterior(
        self, posterior_block: "ProcessBlock", ingredient_name_to_link: str
    ):
        """link the posterior block's ingredient to current material

        Args:
            posterior_block (Block): posterior block containing the ingredient to link
            ingredient_name_to_link (str): _description_
        """
        for name in posterior_block.ingredients.keys():
            if posterior_block.ingredients[name].run.name == ingredient_name_to_link:
                posterior_block.ingredients[name].spec.material = self.material.spec
                posterior_block.ingredients[name].run.material = self.material.run

    @classmethod
    def from_(cls, any):
        if isinstance_base_element(any):
            if isinstance(any, Material):
                self.material = any
            if isinstance(any, Process):
                self.process = any
            elif isinstance(any, Ingredient):
                self.ingredients[any.name] = any
            elif isinstance(any, Measurement):
                self.measurements[any.name] = any
            self.link_within()
        # elif

    def add_ingredient(self, ingredient: Ingredient):
        """add ingredient to block"""
        if not isinstance(ingredient, Ingredient):
            raise TypeError(f"expected 'Ingredient'; got '{type(ingredient)}' ")
        if ingredient.name in self.ingredients.keys():
            raise NameError(
                f"Ingredients must have unique names. Found a duplicate: {ingredient.name}"
            )
        self.ingredients[ingredient.name] = ingredient

    def add_process(self, process: Process):
        """add process to block"""
        if not isinstance(process, Process):
            raise TypeError(f"expected 'Process'; got '{type(process)}' ")
        self.process = process

    def add_material(self, material: Material):
        """add material to block"""
        if not isinstance(material, Material):
            raise TypeError(f"expected 'Material'; got '{type(material)}' ")
        self.material = process

    def add_measurement(self, measurement: Measurement):
        """add measurement to block"""
        if not isinstance(measurement, Measurement):
            raise TypeError(f"expected 'Measurement'; got '{type(measurement)}' ")
        if measurement.name in self.measurements.keys():
            raise NameError(
                f"measurements must have unique names. Found a duplicate: {measurement.name}"
            )
        self.measurements[measurement.name] = measurement
