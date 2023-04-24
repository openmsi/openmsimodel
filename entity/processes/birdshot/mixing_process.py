from typing import ClassVar

from gemd import ProcessTemplate, ParameterTemplate, CategoricalBounds, NominalCategorical

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['MixingProcess']

class MixingProcess(Process):
    '''Class representing the mixing of materials/elements for an experiment '''
    
    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Mixing",
        description='''Mixing individual elements of the composition to make the initial mixture for the alloy 
                '''
    )

    _ATTRS: ClassVar[AttrsDict] = {'conditions': {}, 'parameters': {}}

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Supplier',
    #         bounds=CategoricalBounds(categories=[''])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    finalize_template(_ATTRS, TEMPLATE)
