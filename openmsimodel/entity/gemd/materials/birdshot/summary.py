from typing import ClassVar

from gemd import (
    MaterialTemplate,
    ParameterTemplate,
    CategoricalBounds,
    NominalCategorical,
)

from openmsimodel.entity.gemd.material import Material
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
    _validate_temp_keys,
)

import pandas as pd

# __all__ = ["SummarySheet"]


class Summary(Material):
    """Class representing summary"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        "Summary",
        description="Summary sheet of all the experiments conducted in previous batch that will help generate the next compositions spaces and suggest compositions via Bayesian Optimizization",
    )

    _ATTRS: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Iteration',
    #         bounds=CategoricalBounds(categories=['AAA, AAB, AAC'])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    finalize_template(_ATTRS, TEMPLATE)
