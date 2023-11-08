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
    _validate_temp_keys,
)


class AggregateTravelerSamples(Process):
    """Class representing aggegation of traveler samples"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Aggregate Traveler Samples",
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    finalize_template(_ATTRS, TEMPLATE)
