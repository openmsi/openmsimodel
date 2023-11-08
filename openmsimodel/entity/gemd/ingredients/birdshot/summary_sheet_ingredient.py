from typing import ClassVar

from gemd import ParameterTemplate, CategoricalBounds, NominalCategorical

from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["SummarySheet"]


class SummarySheetIngredient(Ingredient):
    """Class representing summary sheet"""

    # name = __name__ + ' Template'
    # TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
    #     name,
    #     description='Summary sheet of all the experiments conducted in previous batch that will help generate the next compositions spaces and suggest compositions via Bayesian Optimizization',
    # )

    # _ATTRS: ClassVar[AttrsDict] = {'properties': {}}

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Supplier',
    #         bounds=CategoricalBounds(categories=[''])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    # finalize_template(_ATTRS, TEMPLATE)
