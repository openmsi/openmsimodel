from typing import ClassVar

from gemd import ProcessTemplate, ParameterTemplate, CategoricalBounds, NominalCategorical

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['AggregateSummarySheet']

class AggregateSummarySheet(Process):
    '''Class representing aggegation of summary sheet '''
    
    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name='Aggregate Summary Sheet',
        description='''Aggregating what is necessary for the current process, whether that be ingredients for a mixture, 
        a list of characterization results for Bayesian optimization, etc
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
