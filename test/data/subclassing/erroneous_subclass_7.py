from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.material import Material
from gemd import (
    ProcessTemplate,
    MaterialTemplate,
    PropertyTemplate,
    ParameterTemplate,
    CategoricalBounds,
)

from openmsimodel.utilities.attributes import (
    _validate_temp_keys,
    define_attribute,
    finalize_template,
)


# missing _ATTRS b)
class erroneousSubclass7(Material):
    TEMPLATE = MaterialTemplate(
        name="erroneousSubclass7",
    )

    finalize_template(_ATTRS, TEMPLATE)
