from typing import ClassVar

from gemd import (
    ProcessTemplate,
    ParameterTemplate,
    CategoricalBounds,
    NominalCategorical,
    RealBounds,
    NominalReal,
)

from openmsimodel.entity.gemd.process import Process
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
    _validate_temp_keys,
)

__all__ = ["ProcessExample"]


class ProcessExample(Process):
    """Class representing an example of process"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Process template example",
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name="Argon Pressure",
    #         bounds=CategoricalBounds(["850-900", "900-950"]),
    #     ),
    # )

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name="Diffusion",
    #         bounds=CategoricalBounds(categories=["Before Each Melt"]),
    #     ),
    # )

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name="Ingot Location",
    #         bounds=RealBounds(0, 10, ""),
    #     ),
    # )

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name="Initial Purging Times",
    #         bounds=RealBounds(0, 10, "hour"),
    #     ),
    #     default_value=NominalReal(0, "hour"),
    # )

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name="Vacuum Before Melt",
    #         bounds=RealBounds(0, 5, ""),
    #     ),
    #     default_value=NominalReal(0, ""),
    # )

    finalize_template(_ATTRS, TEMPLATE)
