from typing import ClassVar

from gemd import MeasurementTemplate, PropertyTemplate, RealBounds, NominalReal

from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["MeasureDimensions"]


class MeasureDimensions(Measurement):
    """Class representing measurement of diemsniosn as a measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="MeasureDimensions",
        description="The measurement of dimension of an alloy in its form, often ingot",
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Length",
            bounds=RealBounds(0, 100, "cm"),
            description="Length of alloy",
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Width",
            bounds=RealBounds(0, 50, "cm"),
            description="Width of alloy",
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Thickness",
            bounds=RealBounds(0, 25, "cm"),
            description="Thickness of alloy",
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Thickness Reduction",
            bounds=RealBounds(-150, 150, "cm"),
            description="Thickness of alloy",
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
