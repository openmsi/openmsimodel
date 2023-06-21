from typing import ClassVar

from gemd import ProcessTemplate

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['Homogenization']

class Homogenization(Process):
    '''Class representing homogenization cycle '''
    
    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Homogenization",
        description='''Homogenizing
                '''
    )

    _ATTRS: ClassVar[AttrsDict] = {'conditions': {}, 'parameters': {}}

    finalize_template(_ATTRS, TEMPLATE)
