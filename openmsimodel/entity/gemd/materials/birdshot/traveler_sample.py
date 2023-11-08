from typing import ClassVar

from gemd import MaterialTemplate
from openmsimodel.entity.gemd.material import Material
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["TravelerSample"]


class TravelerSample(Material):
    """Class representing a traveler sample, or a single element on the traveler that will
    be detached/intended for a specific characterization"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        name="Traveler Sample", description="Traveler sample"
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
