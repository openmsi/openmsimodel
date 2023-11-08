from typing import ClassVar

from gemd import ProcessTemplate, ParameterTemplate, RealBounds

from openmsimodel.entity.gemd.process import Process
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["Forging"]


class Forging(Process):
    """Class representing forging cycle"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Forging",
        description="""Forging
                """,
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}}

    define_attribute(
        _ATTRS,
        template=ParameterTemplate(
            name="Soak Time",
            bounds=RealBounds(0, 120, "minutes"),
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
            name="Maximum Load Step",
            bounds=RealBounds(0, 200, "Pa"),
        ),
    )

    finalize_template(_ATTRS, TEMPLATE)
