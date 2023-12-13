from typing import ClassVar, Type, Optional
from openmsimodel.science_kit.science_kit import ScienceKit
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.gemd_element import GEMDElement
from openmsimodel.utilities.runnable import Runnable


class Tool(Runnable):
    """Tool represents 1+ Elements that are grouped together for easier instantiation, manipulation, analysis, and more.
    The grouping can be based on any rule or criteria of interest, such as consecutive elements, elements with a logical relationships or simply preference.
    """

    def __init__(
        self, name: str, *, science_kit: ScienceKit = None, self_assign: bool = True
    ):
        """initialization of Tool.

        Args:
            name (str): name of subworkflow
            science_kit (ScienceKit, optional): the science_kit that subworkflow belongs to. Defaults to None.
            self_assign (bool, optional): whether to add the current subworkflow to parent science_kit's dictionary 'subs'. Defaults to True.
        """
        self.name = name
        self.science_kit = science_kit
        if self.science_kit and self_assign:
            self.science_kit.subs[name] = self

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
        Tool = cls(*args)


def main(args=None):
    """
    Main method to run from command line
    """
    Tool.run_from_command_line(args)


if __name__ == "__main__":
    main()
