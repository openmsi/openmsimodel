from typing import ClassVar

from gemd import MeasurementTemplate, PropertyTemplate, RealBounds, NominalReal

from openmsimodel.entity.base.measurement import Measurement
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
    _validate_temp_keys,
)

__all__ = ["MeasurementExample"]


class MeasurementExample(Measurement):
    """Class representing an example of measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="Measurement template example",
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)
    # _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         name="Weighed Mass",
    #         bounds=RealBounds(0, 150, "g"),
    #         description="Weighted Mass",
    #     ),
    #     default_value=NominalReal(0.0, "g"),
    # )

    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         name="Mass Loss",
    #         bounds=RealBounds(0, 50, "g"),
    #         description="Relative mass loss",
    #     ),
    #     default_value=NominalReal(0.0, "g"),
    # )

    finalize_template(_ATTRS, TEMPLATE)
