from openmsimodel.entity.base import Material
from openmsimodel.entity.base.attributes import (
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

__all__ = ["MaterialExample"]


class MaterialExample(Material):
    """Class representing a Material example"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        name="Material",
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         name="Form", bounds=CategoricalBounds(categories=["Ingot"])
    #     ),
    # )

    finalize_template(_ATTRS, TEMPLATE)
