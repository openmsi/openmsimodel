from typing import ClassVar

from gemd import (
    ProcessTemplate,
    ParameterTemplate,
    CategoricalBounds,
    NominalCategorical,
)

from openmsimodel.entity.gemd.process import Process
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
    _validate_temp_keys,
)

# __all__ = ["Summarize"]


class Summarize(Process):
    """Class representing summarizing the different measurements needed for B.O and more, coming mainly from excel sheets"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Summarize",
        description="""Aggregating what is necessary for the current process, whether that be ingredients for a mixture, 
        a list of characterization results for Bayesian optimization, etc
        """,
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Supplier',
    #         bounds=CategoricalBounds(categories=[''])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    finalize_template(_ATTRS, TEMPLATE)
