from typing import ClassVar

from gemd import (
    ProcessTemplate,
    ParameterTemplate,
    CategoricalBounds,
    NominalCategorical,
)

from openmsimodel.entity.gemd.process import Process
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["Mixing"]


class Mixing(Process):
    """Class representing the mixing of materials/elements for an experiment"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Mixing",
        description="""Mixing individual elements of the composition to make the initial mixture for the alloy 
                """,
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}}

    finalize_template(_ATTRS, TEMPLATE)
