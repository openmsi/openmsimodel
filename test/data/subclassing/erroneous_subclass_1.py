from openmsimodel.entity.base import Process, Material
from gemd import (
    ProcessTemplate,
    MaterialTemplate,
    PropertyTemplate,
    ParameterTemplate,
    CategoricalBounds,
)

from openmsimodel.entity.base.attributes import _validate_temp_keys, define_attribute


# wrong template type
class erroneousSubclass1(Material):
    TEMPLATE = ProcessTemplate(
        name="erroneousSubclass1",
    )

    _ATTRS = _validate_temp_keys(TEMPLATE)
