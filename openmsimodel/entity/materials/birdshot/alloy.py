from openmsimodel.entity.base import Material
from openmsimodel.entity.base.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
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

__all__ = ["Alloy"]


class Alloy(Material):
    """Class representing an Alloy"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        name="Alloy",
        description="Alloy generated with a unique composition and synthesis parameters",
    )

    _ATTRS: ClassVar[AttrsDict] = {"properties": {}}

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Form", bounds=CategoricalBounds(categories=["Ingot"])
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
