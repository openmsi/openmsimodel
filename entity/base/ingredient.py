'''Base class for ingredient.'''

from typing import ClassVar, Optional

from gemd import IngredientSpec, IngredientRun, PropertyAndConditions
from gemd.entity.util import make_instance
from gemd.enumeration import SampleType

from .base_node import BaseNode
from .typing import ProcessDict, PropsAndCondsDict
from .process import Process

__all__ = ['Ingredient']

class Ingredient(BaseNode):
    '''
    Base class for ingredients.

    TODO: instructions for subclassing
    '''

    _SpecType = IngredientSpec
    _RunType = IngredientRun