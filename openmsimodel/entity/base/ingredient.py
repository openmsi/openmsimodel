"""Base class for ingredient."""

from abc import ABC
from typing import ClassVar, Optional
from .typing import Spec, Run

from gemd import IngredientSpec, IngredientRun, PropertyAndConditions
from gemd.entity.util import make_instance
from gemd.enumeration import SampleType

from .base_element import BaseElement
from .typing import ProcessDict, PropsAndCondsDict
from .process import Process

__all__ = ["Ingredient"]


class Ingredient(BaseElement):
    """
    Base class for ingredients.

    """

    _SpecType = IngredientSpec
    _RunType = IngredientRun

    def __init__(self, name: str, *, notes: Optional[str] = None) -> None:
        # BaseElement.__init__(self, name)
        super(ABC, self).__init__()
        self.name = name
        self._spec: Spec = self._SpecType(name=name, notes=notes)
        self._run: Run = make_instance(self._spec)

    @property
    def spec(self) -> IngredientSpec:
        """The underlying process spec."""
        return self._spec

    @property
    def run(self) -> IngredientRun:
        """The underlying process run."""
        return self._run

    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: IngredientSpec = None,
        run: IngredientRun = None
    ) -> "Process":
        """
        Instantiate a `Process` from a spec or run with appropriate validation.

        Note that the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        """
        pass

    def to_form(self) -> str:
        pass

    # TODO: from_material
    # TODO: from_material_run_or_spec
