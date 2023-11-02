from openmsimodel.entity.base.process import Process
from openmsimodel.entity.base.process import Material
from gemd import (
    ProcessTemplate,
    MaterialTemplate,
    PropertyTemplate,
    ParameterTemplate,
    CategoricalBounds,
)

from openmsimodel.utilities.attributes import _validate_temp_keys, define_attribute


# wrong attribute template type
class erroneousSubclass2(Process):
    TEMPLATE = ProcessTemplate(
        name="erroneousSubclass2",
    )

    _ATTRS = _validate_temp_keys(TEMPLATE)

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Form",
            bounds=CategoricalBounds(["Solid", "Liquid"]),
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
