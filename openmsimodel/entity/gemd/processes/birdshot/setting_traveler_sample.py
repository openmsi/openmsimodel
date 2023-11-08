from typing import ClassVar

from gemd import ProcessTemplate

from openmsimodel.entity.gemd.process import Process
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["SettingTravelerSample"]


class SettingTravelerSample(Process):
    """Class representing singular sample extraction from sample"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Setting Traveler Sample",
        description="""extracting a single sample, such as T01, from the traveler
                """,
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}}

    finalize_template(_ATTRS, TEMPLATE)
