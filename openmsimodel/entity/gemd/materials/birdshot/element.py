from typing import ClassVar

from gemd import (
    MaterialTemplate,
    PropertyTemplate,
    CategoricalBounds,
    NominalCategorical,
)
from gemd.entity.bounds import RealBounds
from gemd.entity.value import NominalReal

from openmsimodel.entity.gemd.material import Material
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["Element"]


class Element(Material):
    """Class representing element"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        "Element",
        description="Individual ingredient of a composition",
    )

    _ATTRS: ClassVar[AttrsDict] = {"properties": {}}

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            "Composition Percentage",
            bounds=RealBounds(0, 100, ""),
            description="Percentage of the total composition that the material takes in the overall composition",
        ),
        default_value=NominalReal(0.0, ""),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            "Target Mass",
            bounds=RealBounds(0, 150, "g"),
            description="Expected mass to attain based on composition design ",
        ),
        default_value=NominalReal(0.0, "g"),
    )

    finalize_template(_ATTRS, TEMPLATE)
