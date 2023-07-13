'''Base class for ingredient.'''

from abc import ABC
from typing import ClassVar, Optional
from .typing import Spec, Run

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
    
    def __init__(self, name: str, *, notes: Optional[str] = None) -> None:

        super(ABC, self).__init__()
        self._spec: Spec = self._SpecType(name=name, notes=notes)
        self._run: Run = make_instance(self._spec)
    
    @property
    def spec(self) -> IngredientSpec:
        '''The underlying process spec.'''
        return self._spec

    @property
    def run(self) -> IngredientRun:
        '''The underlying process run.'''
        return self._run
    
    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: IngredientSpec = None,
        run: IngredientRun = None
        ) -> 'Process':
        '''
        Instantiate an `Ingredient` from a spec or run with appropriate validation.

        Note that the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        '''
        if spec is None and run is None:
            raise ValueError('At least one of spec or run must be given.')

        ingredient = cls(name, notes=notes)

        if spec is not None:

            if not isinstance(spec, IngredientSpec):
                raise TypeError('spec must be a MeasurementSpec.')

            ingredient._spec = spec

            ingredient.spec.name = name
            ingredient.spec.notes = notes

        if run is not None:

            if not isinstance(run, IngredientRun):
                raise TypeError('run must be a MeasurementRun.')

            ingredient._run = run

            # ingredient._run.name = name
            ingredient.run.notes = notes
            ingredient.run.spec = ingredient.spec

        else:
            ingredient.run = make_instance(ingredient.spec)

        return ingredient
        

    def to_form(self) -> str:
        pass
