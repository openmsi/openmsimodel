from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.gemd_base_element import GEMDElement
from openmsimodel.subworkflow.subworkflow import Subworkflow
from typing import ClassVar, Type, Optional
from openmsimodel.entity.gemd.helpers import from_spec_or_run
from openmsimodel.utilities.typing import Spec, Run


class ProcessBlock(Subworkflow):
    """
    ProcessBlock is a type of Subworkflow intended to represent consecutive Elements in the order of 'Ingredients', 'Process', 'Material', and 'Measurements'.
    It is the natural order of GEMD objects, and of our Elements object, which are essentially GEMD wrappers. It is a loose class and can omit some elements of the block.
    It can be a powerful way to manipulate, link, dump, etc, GEMD objects together, while Blocks themselves can be linked with one another, facilitating repeat
    elements, linking for wide (i.e., many ingredients, many measurements) or vertical (i.e., long sequence of Elements) workflow, etc.
    """

    @property
    def assets(self) -> list:
        _all = []
        for i in self.ingredients.values():
            _all.append(i)
        if self.process:
            _all.append(self.process)
        if self.material:
            _all.append(self.material)
        for m in self.measurements.values():
            _all.append(m)
        return _all

    @property
    def gemd_assets(self) -> list:
        _all_gemd = []
        for obj in self.assets:
            _all_gemd.extend(obj.assets)
        return _all_gemd

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
        _type: str = None,
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
        self.type = _type

    def link_within(self):
        """this functions links the specs and runs of the Elements in the current block."""
        # link ingredients to process
        if self.ingredients and self.process:
            for name in self.ingredients.keys():
                self.ingredients[name].spec.process = self.process.spec
                self.ingredients[name].run.process = self.process.run
        else:
            print(f"no ingredients and process for block '{self.name}' were linked. ")
        # link process to material
        if self.material and self.process:
            self.material.spec.process = self.process.spec
            self.material.run.process = self.process.run
        else:
            print(f"no material and process for block '{self.name}' were linked. ")
        # link measurements to material
        if self.measurements and self.material:
            for name in self.measurements.keys():
                self.measurements[name].run.material = self.material.run
        # else:
        #     print(f"measurements and material for block {self.name} were not linked. ")

    def link_prior(
        self, prior_block: "ProcessBlock", ingredient_name_to_link: str
    ):  # TODO: change to 'current_ing_name'
        """links the prior block's material to current ingredient.

        Args:
            prior_block (Block): prior block containing the material to link
            ingredient_name_to_link (str): name of the ingredient in current block to link to prior material
        """
        linked = False
        for name in self.ingredients.keys():
            if self.ingredients[name].run.name == ingredient_name_to_link:
                self.ingredients[name].spec.material = prior_block.material.spec
                self.ingredients[name].run.material = prior_block.material.run
                linked = True
        if not linked:
            print(
                f"Current block '{self.name}' couldn't be linked to block '{prior_block.name}'"
            )

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

    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: Spec = None,
        run: Run = None,
    ):
        initial = from_spec_or_run(name=name, notes=notes, spec=spec, run=run)
        # if isinstance(initial, Material):

    # @classmethod
    # def from_(self, any):
    #     if isinstance_base_element(any):
    #         if isinstance(any, Material):
    #             self.material = any
    #         if isinstance(any, Process):
    #             self.process = any
    #         elif isinstance(any, Ingredient):
    #             self.ingredients[any.name] = any
    #         elif isinstance(any, Measurement):
    #             self.measurements[any.name] = any
    #         self.link_within()
    # elif isinstance_all_gemd(any):
    #     if isinstance(any, Material):
