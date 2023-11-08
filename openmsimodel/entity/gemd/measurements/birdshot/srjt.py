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
    _validate_temp_keys,
)


class SRJT(Measurement):
    """Class representing SRJT as a measurement"""

    TEMPLATE: ClassVar[MeasurementTemplate] = MeasurementTemplate(
        name="SRJT", description="Strain rate jump measurement"
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Avg. Corrected Hardness (Gpa)", bounds=RealBounds(0, 5, "GPa")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Corrected Hardness Std. Dev.", bounds=RealBounds(0, 1, "")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Corrected Modulus Std. Dev.", bounds=RealBounds(0, 1, "")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Avg. Corrected Modulus (Gpa)", bounds=RealBounds(0, 400, "GPa")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Avg. Pile-up Ratio", bounds=RealBounds(0, 200, "")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Avg. Raw Modulus (Gpa)", bounds=RealBounds(0, 500, "GPa")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Avg. Raw Hardness (Gpa)", bounds=RealBounds(0, 5, "GPa")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Strain Rate Sensitivity Exponent", bounds=RealBounds(0, 1, "")
        ),
    )

    define_attribute(
        _ATTRS,
        template=PropertyTemplate(
            name="Strain Rate Sensitivity Exponent Std. Dev.",
            bounds=RealBounds(0, 1, ""),
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
