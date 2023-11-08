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

__all__ = ["InferCompositions"]


class InferCompositions(Process):
    """Class representing the inference of compositions via BO"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Infer Compositions",
        description="""Applying Bayezian Optimization based on multi-inputs/multi-output
        objectives to generated new composition space, with data extracted 
        from summary sheet aggregated by various experimental teams
        """,
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}}

    finalize_template(_ATTRS, TEMPLATE)
