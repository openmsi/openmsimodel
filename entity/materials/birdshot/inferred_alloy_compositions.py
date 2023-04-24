from typing import ClassVar

from gemd import MaterialTemplate, ParameterTemplate, CategoricalBounds, NominalCategorical

from entity.base import Material
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['InferredAlloyCompositions']

class InferredAlloyCompositions(Material):
    '''Class representing suggested compositions'''
    
    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        'Inferred Alloy Compositions',
        description='Final selection of the bayesian optimziation algorithm, which can generate different number of compositions (i.e., 16 for VAM, 8 for DED) under various paramereters',
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
