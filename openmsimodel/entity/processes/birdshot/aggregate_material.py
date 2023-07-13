from typing import ClassVar

from gemd import ProcessTemplate, ParameterTemplate, CategoricalBounds, NominalCategorical

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['AggregateMaterial']

class AggregateMaterial(Process):
    '''Class representing the aggregation of materials/elements for an experiment '''
    
    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Aggregate Material",
        description='''Aggregaging the correct ingredients to produce a mixture that can go through
                fabrication procedure
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
