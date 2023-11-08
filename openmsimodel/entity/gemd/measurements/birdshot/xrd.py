from typing import ClassVar

from gemd import (
    MeasurementTemplate,
    PropertyTemplate,
    CategoricalBounds,
    NominalCategorical,
    RealBounds,
    NominalReal,
)
from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["XRD"]


class XRD(Measurement):
    """Class representing XRD as a measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="XRD", description="XRD measurement"
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Lattice Parameter", bounds=RealBounds(0, 5, "cm")
        ),
        # default_value=NominalReal(0, "cm"),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Phase", bounds=CategoricalBounds(categories=["FCC"])
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Hardness, HV", bounds=RealBounds(0, 1000, "Pa")
        ),
        # default_value=NominalReal(0, "Pa"),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(name="SD, HV", bounds=RealBounds(0, 1000, "Pa")),
        # default_value=NominalReal(0, "Pa"),
    )

    finalize_template(_ATTRS, TEMPLATE)
