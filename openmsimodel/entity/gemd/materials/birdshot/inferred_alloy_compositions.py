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

__all__ = ["InferredAlloyCompositions"]


class InferredAlloyCompositions(Material):
    """Class representing suggested compositions"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        "Inferred Alloy Compositions",
        description="Final selection of the bayesian optimziation algorithm, which can generate different number of compositions (i.e., 16 for VAM, 8 for DED) under various paramereters",
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
