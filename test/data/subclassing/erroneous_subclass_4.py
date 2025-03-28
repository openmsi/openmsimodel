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


class erroneousSubclass4(Material):
    finalize_template(_ATTRS, TEMPLATE)
