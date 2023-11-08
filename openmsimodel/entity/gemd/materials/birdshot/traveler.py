from typing import ClassVar

from gemd import MaterialTemplate
from openmsimodel.entity.gemd.material import Material
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["Traveler"]


class Traveler(Material):
    """Class representing a traveler"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        name="Traveler", description="Traveler"
    )

    _ATTRS: ClassVar[AttrsDict] = {"properties": {}}

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Supplier',
    #         bounds=CategoricalBounds(categories=[''])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    finalize_template(_ATTRS, TEMPLATE)
