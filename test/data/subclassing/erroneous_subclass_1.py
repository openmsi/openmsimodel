from openmsimodel.entity.base.process import Process
from openmsimodel.entity.base.material import Material
from openmsimodel.utilities.attributes import _validate_temp_keys, define_attribute

from gemd import (
    ProcessTemplate,
    MaterialTemplate,
    PropertyTemplate,
    ParameterTemplate,
    CategoricalBounds,
)


# wrong template type
class erroneousSubclass1(Material):
    TEMPLATE = ProcessTemplate(
        name="erroneousSubclass1",
    )

    _ATTRS = _validate_temp_keys(TEMPLATE)
