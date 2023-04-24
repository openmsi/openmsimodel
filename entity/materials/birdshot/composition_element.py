from typing import ClassVar

from gemd import MaterialTemplate, PropertyTemplate, CategoricalBounds, NominalCategorical
from gemd.entity.bounds import RealBounds
from gemd.entity.value import NominalReal

from entity.base import Material
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ['CompositionElement']

class CompositionElement(Material):
    '''Class representing composition element'''
    
    TEMPLATE: ClassVar[MaterialTemplate] = MaterialTemplate(
        'Composition Element',
        description='Individual ingredient of a composition',
    )

    _ATTRS: ClassVar[AttrsDict] = {'properties': {}}

    finalize_template(_ATTRS, TEMPLATE)
