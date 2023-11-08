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


class Alloy(Material):
    """Class representing an Alloy"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        name="Alloy",
        description="Alloy generated with a unique composition and synthesis parameters",
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Form", bounds=CategoricalBounds(categories=["Ingot"])
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
