from typing import ClassVar

from gemd import (
    MeasurementTemplate,
    PropertyTemplate,
    CategoricalBounds,
    NominalCategorical,
)
from entity.base import Measurement
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ["SEM"]


class SEM(Measurement):
    """Class representing SEM as a measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="SEM", description="SEM Characterization"
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    

    finalize_template(_ATTRS, TEMPLATE)
