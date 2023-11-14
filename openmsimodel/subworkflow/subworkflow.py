from typing import ClassVar, Type, Optional
from openmsimodel.workflow.workflow import Workflow
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.gemd_base_element import GEMDElement
from openmsimodel.utilities.runnable import Runnable


class Subworkflow(Runnable):
    """Subworkflow represents 1+ Elements that are grouped together for easier instantiation, manipulation, analysis, and more.
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
        if self.workflow and self_assign:
            self.workflow.subs[name] = self

    @classmethod
    def from_(self, any):
        """returns a subworkflow instantiated from elements contained it. will vary based on subworkflow and element types."""
        pass

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
