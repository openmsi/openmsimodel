from typing import ClassVar

from gemd import (
    ProcessTemplate,
    ParameterTemplate,
    CategoricalBounds,
    NominalCategorical,
    RealBounds,
    NominalReal,
)

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ["Homogenization"]


class Homogenization(Process):
    """Class representing homogenization cycle"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Homogenization",
        description="""Homogenizing
                """,
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}}

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Pressure",
            bounds=RealBounds(0, 20, "Pa"),
        ),
    )

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Duration",
            bounds=RealBounds(0, 72, "hours"),
        ),
    )

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Temperature",
            bounds=RealBounds(0, 2000, "Kelvin"),
        ),
    )

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Atmosphere",
            bounds=CategoricalBounds(["Ar"]),
        ),
    )

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Cooling Rate",
            bounds=CategoricalBounds(["FC"]),
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
