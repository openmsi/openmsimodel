from openmsimodel.entity.base.process import Process
from openmsimodel.entity.base.material import Material
from gemd import (
    ProcessTemplate,
    MaterialTemplate,
    PropertyTemplate,
    ParameterTemplate,
    CategoricalBounds,
)

from openmsimodel.utilities.attributes import _validate_temp_keys, define_attribute


# missing _ATTRS a)
class erroneousSubclass6(Material):
    TEMPLATE = MaterialTemplate(
        name="erroneousSubclass6",
    )

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Pressure",
            bounds=CategoricalBounds(["0.1-0.2", "0.2-0.3"]),
        ),
    )
