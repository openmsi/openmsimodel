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


class AddMaterial(Process):
    """Class representing the aggregation of materials/elements for an experiment"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Add Material",
        description="""Adding the correct ingredients to produce a mixture that can go through
                fabrication procedure
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
