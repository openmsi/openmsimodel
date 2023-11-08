from typing import ClassVar

from gemd import MeasurementTemplate, PropertyTemplate, RealBounds, NominalReal

from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["Weighting"]


class Weighting(Measurement):
    """Class representing weighting as a measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="Weighting", description="The measurement of weight"
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Weighed Mass",
            bounds=RealBounds(0, 150, "g"),
            description="Weighted Mass",
        ),
        default_value=NominalReal(0.0, "g"),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Mass Loss",
            bounds=RealBounds(0, 50, "g"),
            description="Relative mass loss",
        ),
        default_value=NominalReal(0.0, "g"),
    )

    finalize_template(_ATTRS, TEMPLATE)
