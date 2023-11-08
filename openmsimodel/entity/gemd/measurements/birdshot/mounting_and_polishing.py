from typing import ClassVar

from gemd import MeasurementTemplate

from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["MountingAndPolishing"]


class MountingAndPolishing(Measurement):
    """Class representing mounting and polishing"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="Mounting And Polishing",
        description="The process of mounting and polishing",
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Supplier',
    #         bounds=CategoricalBounds(categories=[''])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    finalize_template(_ATTRS, TEMPLATE)
