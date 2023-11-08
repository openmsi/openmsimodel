from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.material import Material
from gemd import (
    ProcessTemplate,
    MaterialTemplate,
    PropertyTemplate,
    ParameterTemplate,
    CategoricalBounds,
)

from openmsimodel.utilities.attributes import _validate_temp_keys, define_attribute


# wrong attribute template type, 2)
class erroneousSubclass3(Material):
    TEMPLATE = MaterialTemplate(
        name="erroneousSubclass3",
    )

    _ATTRS = _validate_temp_keys(TEMPLATE)

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Pressure",
            bounds=CategoricalBounds(["0.1-0.2", "0.2-0.3"]),
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
