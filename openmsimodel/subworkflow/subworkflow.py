from typing import ClassVar, Type, Optional
from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.base.material import Material
from openmsimodel.entity.base.base_element import BaseElement
from openmsimodel.utilities.runnable import Runnable


class Subworkflow(Runnable):
    """
    Subworkflow represents 1+ BaseElements that are grouped together for easier instantiation, manipulation, analysis, and more.
    The grouping can be based on any rule or criteria of interest, such as consecutive elements, elements with a logical relationships or simply preference.
    """

    def __init__(
        self, name: str, *, workflow: Workflow = None, self_assign: bool = True
    ):
        """initialization of Subworkflow.

        Args:
            name (str): name of subworkflow
            workflow (Workflow, optional): the workflow that subworkflow belongs to. Defaults to None.
            self_assign (bool, optional): whether to add the current subworkflow to parent workflow's dictionary 'subs'. Defaults to True.
        """
        self.name = name
        self.workflow = workflow
        if self_assign:
            self.workflow.subs[name] = self

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = []
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        Subworkflow = cls(*args)


def main(args=None):
    """
    Main method to run from command line
    """
    Subworkflow.run_from_command_line(args)


if __name__ == "__main__":
    main()

    # def thin_dumps(self, encoder, destination):
    #     for ingredient in self.ingredients:
    #         ingredient.thin_dumps(encoder, destination)
    #     if self.process:
    #         self.process.thin_dumps(encoder, destination)
    #     if self.material:
    #         self.material.thin_dumps(encoder, destination)
    #     for measurement in self.measurements:
    #         measurement.thin_dumps(encoder, destination)

    # def dumps(self, encoder, destination):
    #     for ingredient in self.ingredients:
    #         ingredient.dumps(encoder, destination)
    #     if self.process:
    #         self.process.dumps(encoder, destination)
    #     if self.material:
    #         self.material.dumps(encoder, destination)
    #     for measurement in self.measurements:
    #         measurement.dumps(encoder, destination)

    # def link_within(self):
    #     # link ingredients to process
    #     if self.ingredients and self.process:
    #         for i in self.ingredients:
    #             i._spec.process = self.process._spec
    #             i._run.process = self.process._run
    #     # link process to material
    #     if self.material and self.process:
    #         self.material._spec.process = self.process._spec
    #         self.material._run.process = self.process._run
    #     # link measurements to material
    #     if self.measurements and self.material:
    #         for m in self.measurements:
    #             m._run.material = self.material._run

    # def link_prior(self, prior_block, ingredient_name_to_link):
    #     # links the prior block's material to current ingredient
    #     for i, _ in enumerate(self.ingredients):
    #         # print(self.ingredients[i]._run.name)
    #         # print(ingredient_name_to_link)
    #         if self.ingredients[i]._run.name == ingredient_name_to_link:
    #             self.ingredients[i]._spec.material = prior_block.material._spec
    #             self.ingredients[i]._run.material = prior_block.material._run
    #             # print("completed")

    # def link_posterior(self, posterior_block, ingredient_name_to_link):
    #     # link the posterior block's ingredient to current material
    #     for i in posterior_block.ingredients:
    #         if i._run.name == ingredient_name_to_link:
    #             i._spec.material = self.material._spec
    #             i._run.material = self.material._run

    # def add_ingredient(self):
    #     pass

    # def add_process(self):
    #     pass

    # def add_material(self):
    #     pass

    # def add_measurement(self):
    #     pass
