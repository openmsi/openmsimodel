from openmsimodel.entity.gemd.material import Material
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
    _validate_temp_keys,
)

from typing import ClassVar

from gemd import (
    MaterialTemplate,
    PropertyTemplate,
    CategoricalBounds,
    NominalCategorical,
    RealBounds,
    NominalReal,
)


class TravelerSamples(Material):
    """Class representing grouped traveler samples"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        name="Traveler Samples",
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    finalize_template(_ATTRS, TEMPLATE)
