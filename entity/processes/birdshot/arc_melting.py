from typing import ClassVar

from gemd import ProcessTemplate

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['ArcMelting']

class ArcMelting(Process):
    '''Class representing arc melting '''
    
    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Arc Melting",
        description='''One of the fabrication methods, arc melting
                '''
    )

    _ATTRS: ClassVar[AttrsDict] = {'conditions': {}, 'parameters': {}}

    finalize_template(_ATTRS, TEMPLATE)
