from typing import ClassVar

from gemd import MaterialTemplate, ParameterTemplate, CategoricalBounds, NominalCategorical

from entity.base import Material
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

import pandas as pd

__all__ = ['SummarySheet']

class SummarySheet(Material):
    '''Class representing summary sheet '''
    
    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        'Summary Sheet',
        description='Summary sheet of all the experiments conducted in previous batch that will help generate the next compositions spaces and suggest compositions via Bayesian Optimizization',
    )

    _ATTRS: ClassVar[AttrsDict] = {'properties': {}}

    # define_attribute(
    #     _ATTRS,
    #     template=ParameterTemplate(
    #         name='Iteration',
    #         bounds=CategoricalBounds(categories=['AAA, AAB, AAC'])
    #     ),
    #     default_value=NominalCategorical('')
    # )

    finalize_template(_ATTRS, TEMPLATE)
    
    
        
