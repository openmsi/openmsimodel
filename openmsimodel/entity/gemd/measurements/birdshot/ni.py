from typing import ClassVar

from gemd import MeasurementTemplate

from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["NI"]


class NI(Measurement):
    """Class representing NI as a measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="NI", description="NI measurement"
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    finalize_template(_ATTRS, TEMPLATE)
