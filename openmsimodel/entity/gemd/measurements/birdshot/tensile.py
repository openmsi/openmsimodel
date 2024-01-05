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

__all__ = ["Tensile"]


class Tensile(Measurement):
    """Class representing Tensile as a measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="Tensile", description="Tensile measurement"
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}, "properties": {}}

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Elastic Modulus, GPa", bounds=RealBounds(0, 500, "GPa")
        ),
        default_value=NominalReal(0, "GPa")
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Yield Strength, MPa", bounds=RealBounds(-10000, 10000, "MPa")
        ),
        default_value=NominalReal(0, "MPa")
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="UTS, MPa", bounds=RealBounds(-10000, 10000, "MPa")
        ),
        default_value=NominalReal(0, "MPa")
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(name="Elongation, %", bounds=RealBounds(0, 100, "")),
        default_value=NominalReal(0, "MPa")
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Strain Hardening, MPa", bounds=RealBounds(-10000, 10000, "MPa")
        ),
        default_value=NominalReal(0, "MPa")
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(name="dUTS_dY", bounds=RealBounds(0, 100, "")),
        default_value=NominalReal(0, "MPa")
    )

    finalize_template(_ATTRS, TEMPLATE)
