from typing import ClassVar

from gemd import (
    MaterialTemplate,
    PropertyTemplate,
    CategoricalBounds,
    NominalCategorical,
    RealBounds,
    NominalReal,
)
from entity.base import Material
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

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

    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         name="Mass",
    #         bounds=RealBounds(0, 150, "g"),
    #     ),
    #     default_value=NominalReal(0.0, "g"),
    # )

    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         name="Mass Loss",
    #         bounds=RealBounds(0, 50, "g"),
    #     ),
    #     default_value=NominalReal(0.0, "g"),
    # )

    finalize_template(_ATTRS, TEMPLATE)
