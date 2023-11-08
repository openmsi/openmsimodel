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

__all__ = ["SelectComposition"]


class SelectComposition(Process):
    """Class representing the selection of a composition among the choices"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Select Composition",
        description="""Selecting a composition from suggested compositions by Bayesian inference
                """,
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}}

    finalize_template(_ATTRS, TEMPLATE)
