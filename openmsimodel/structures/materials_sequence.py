from openmsimodel.science_kit.science_kit import ScienceKit
from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.gemd_element import GEMDElement
from openmsimodel.structures.structure import Structure
from typing import ClassVar, Type, Optional
from openmsimodel.entity.gemd.helpers import from_spec_or_run
from openmsimodel.utilities.typing import Spec, Run


class MaterialsSequence(Structure):
    """
    MaterialsSequence is a type of Structure intended to represent consecutive Elements in the order of 'Ingredients', 'Process', 'Material', and 'Measurements'.
    It is the natural order of GEMD objects, and of our Elements object, which are essentially GEMD wrappers. It is a loose class and can omit some elements of the block.
    It can be a powerful way to manipulate, link, dump, etc, GEMD objects together, while Blocks themselves can be linked with one another, facilitating repeat
    elements, linking for wide (i.e., many ingredients, many measurements) or vertical (i.e., long sequence of Elements) science_kit, etc.
    """

    def __init__(  # FIXME
        self,
        name: str,
        science_kit: ScienceKit = None,
        ingredients: Optional[
            dict
        ] = {},  # TODO: names have to be unique? will that be a problem?
        process: Optional[Process] = None,
        material: Optional[Material] = None,
        measurements: Optional[dict] = {},
        _type: str = None,
    ):  # FIXME
        """elementization of MaterialsSequence.

        Args:
            name (str): Block name
            process (Optional[Process]): process of block.
            science_kit (ScienceKit, optional): science_kit that block belongs to. Defaults to None.
            material (Optional[Material], optional): material of block. Defaults to None.
            ingredients (Optional[list, dict], optional): Ingredients of block. Defaults to {}.
            measurements (Optional[list,dict], optional): Ingredients of block. Defaults to {}.

        Raises:
            TypeError: 'process' argument is not set.
            TypeError: ingredients must be of type "dict".
            TypeError: measurement must be of type "dict".
        """

        Structure.__init__(self, name, science_kit=science_kit)
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

    @property
    def element_assets(self) -> list:
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
    def assets(self) -> list:
        _all_gemd = []
        for obj in self.element_assets:
            _all_gemd.extend(obj.assets)
        return _all_gemd

    #######################################

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
        self, prior_block: "MaterialsSequence", ingredient_name_to_link: str
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
        self, posterior_block: "MaterialsSequence", ingredient_name_to_link: str
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
        process = None
        material = None
        traversed = {
            "process": False,
            "measurements": False,
            "material": False,
            "ingredients": False,
        }
        ingredients = set()
        measurements = set()

        initial = from_spec_or_run(name=name, notes=notes, spec=spec, run=run)

        if initial.__class__.__name__ == "Process":
            process = initial
        elif initial.__class__.__name__ == "Material":
            material = initial
        elif initial.__class__.__name__ == "Ingredient":
            ingredients.add(initial)
        elif initial.__class__.__name__ == "Measurement":
            measurements.add(initial)

        def traverse(element):
            nonlocal traversed, material, process, ingredients, measurements
            if isinstance(element, Material):  #
                if hasattr(element.run, "measurements"):
                    if not traversed["measurements"]:
                        traversed["measurements"] = True
                        for measurement_run in element.run.measurements:
                            measurements.add(
                                Measurement.from_spec_or_run(
                                    name=measurement_run.name,
                                    run=measurement_run,
                                    spec=measurement_run.spec,
                                )
                            )
                if hasattr(element.run, "process"):
                    obj = element.run.process
                    process = Process.from_spec_or_run(
                        name=obj.name, run=obj, spec=obj.spec
                    )
                    if not traversed["process"]:
                        traversed["process"] = True
                        traverse(process)
            elif isinstance(element, Process):  #
                if hasattr(element.run, "output_material"):
                    obj = element.run.output_material
                    material = Material.from_spec_or_run(
                        name=obj.name,
                        run=obj,
                        spec=obj.spec,
                    )
                    # FIXME: must be put prior but can cause issues since traverse hasn't techincally been successfully executed
                    if not traversed["material"]:
                        traversed["material"] = True
                        traverse(material)

                if hasattr(element.run, "ingredients"):
                    if not traversed["ingredients"]:
                        traversed["ingredients"] = True
                        for i, ingredient_run in enumerate(element.run.ingredients):
                            ingredients.add(
                                Ingredient.from_spec_or_run(
                                    ingredient_run.name,
                                    run=ingredient_run,
                                    spec=ingredient_run.spec,
                                )
                            )
            elif isinstance(element, Ingredient):  #
                if hasattr(element.run, "process"):
                    obj = element.run.process
                    process = Process.from_spec_or_run(
                        name=obj.name, run=obj, spec=obj.spec
                    )
                    if not traversed["process"]:
                        traversed["process"] = True
                        traverse(process)
            elif isinstance(element, Measurement):  #
                if hasattr(element.run, "material"):
                    obj = element.run.material
                    material = Material.from_spec_or_run(
                        name=obj.name, run=obj, spec=obj.spec
                    )
                    if not traversed["material"]:
                        traversed["material"] = True
                        traverse(material)

        traverse(initial)
        block = cls(
            name=name,
            process=process,
            science_kit=None,
            material=material,
            ingredients=list(ingredients),
            measurements=list(measurements),
        )
        block.link_within()
        return block
