from typing import ClassVar

from gemd import MaterialTemplate
from entity.base import Material
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['Alloy']

class Alloy(Material):
    '''Class representing an Alloy '''
    
    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        name="Alloy",
        description='Alloy generated with a unique composition and synthesis parameters'
    )

    _ATTRS: ClassVar[AttrsDict] = {'properties': {}}

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Supplier',
    #         bounds=CategoricalBounds(categories=[''])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    finalize_template(_ATTRS, TEMPLATE)
