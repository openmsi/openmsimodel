from typing import ClassVar

from gemd import (
    MaterialTemplate,
    PropertyTemplate,
    CategoricalBounds,
    NominalCategorical,
)
from gemd.entity.bounds import RealBounds
from gemd.entity.value import NominalReal

from openmsimodel.entity.gemd.material import Material
from openmsimodel.utilities.attributes import (
    AttrsDict,
    define_attribute,
    finalize_template,
)

__all__ = ["Composition"]


class Composition(Material):
    """Class representing composition"""

    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        "Alloy Composition",
        description="Composition selected to be fabricated and characterized",
    )

    _ATTRS: ClassVar[AttrsDict] = {"properties": {}}

    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         'Al',
    #         bounds=RealBounds(0,100,''),
    #         description='Percentage of the total composition that Al takes'
    #     ),
    #     default_value=NominalReal(0.0,'')
    # )
    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         'Cr',
    #         bounds=RealBounds(0,100,''),
    #         description='Percentage of the total composition that Cr takes'
    #     ),
    #     default_value=NominalReal(0.0,'')
    # )
    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         'Co',
    #         bounds=RealBounds(0,100,''),
    #         description='Percentage of the total composition that Co takes'
    #     ),
    #     default_value=NominalReal(0.0,'')
    # )
    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         'Fe',
    #         bounds=RealBounds(0,100,''),
    #         description='Percentage of the total composition that Fe takes'
    #     ),
    #     default_value=NominalReal(0.0,'')
    # )
    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         'Ni',
    #         bounds=RealBounds(0,100,''),
    #         description='Percentage of the total composition that Ni takes'
    #     ),
    #     default_value=NominalReal(0.0,'')
    # )
    # define_attribute(
    #     _ATTRS,
    #     template=PropertyTemplate(
    #         'V',
    #         bounds=RealBounds(0,100,''),
    #         description='Percentage of the total composition that V takes'
    #     ),
    #     default_value=NominalReal(0.0,'')
    # )

    finalize_template(_ATTRS, TEMPLATE)
