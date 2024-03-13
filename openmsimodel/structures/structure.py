from abc import ABC, abstractmethod
from openmsimodel.science_kit.science_kit import ScienceKit


class Structure(ABC):

    def __init__(
        self, name: str, *, science_kit: ScienceKit = None, self_assign: bool = True
    ):
        """initialization of Structure.

        Args:
            name (str): name of subworkflow
            science_kit (ScienceKit, optional): the science_kit that subworkflow belongs to. Defaults to None.
            self_assign (bool, optional): whether to add the current subworkflow to parent science_kit's dictionary 'subs'. Defaults to True.
        """
        self.name = name
        self.science_kit = science_kit
        if self.science_kit and self_assign:
            self.science_kit.structures[name] = self
