from typing import ClassVar

from gemd import ProcessTemplate

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['SettingTraveler']

class SettingTraveler(Process):
    '''Class representing the set up of traveler'''
    
    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Setting traveler",
        description='''Setting traveler
                '''
    )

    _ATTRS: ClassVar[AttrsDict] = {'conditions': {}, 'parameters': {}}

    finalize_template(_ATTRS, TEMPLATE)
