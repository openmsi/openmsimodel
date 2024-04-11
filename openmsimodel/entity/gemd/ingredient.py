"""Base class for ingredient."""

from abc import ABC
from typing import ClassVar, Optional

from openmsimodel.utilities.typing import Spec, Run

# from openmsimodel.utilities.typing import ingredientDict, PropsAndCondsDict
from openmsimodel.utilities.typing import Template
from gemd import IngredientSpec, IngredientRun, PropertyAndConditions
from gemd.entity.util import make_instance
from gemd.enumeration import SampleType
from openmsimodel.entity.gemd.impl import assign_uuid
from openmsimodel.entity.gemd.gemd_element import GEMDElement


class Ingredient(GEMDElement):
    """
    Base element for ingredients.

    """

    _SpecType = IngredientSpec
    _RunType = IngredientRun

    def __init__(self, name: str, *, notes: Optional[str] = None) -> None:
        super().__init__(name, notes=notes, is_not_ingredient=False)
        self.name = name
        self._spec: Spec = self._SpecType(name=name, notes=notes)
        self._run: Run = make_instance(self._spec)
        assign_uuid(self._spec, "auto")
        assign_uuid(self._run, "auto")  # redundant?

    @property
    # @abstractmethod
    def template(self) -> Template:
        """The underlying GEMD template."""
        return self.TEMPLATE

    @property
    # @abstractmethod
    def spec(self) -> Spec:
        """The underlying GEMD spec."""
        return self._spec

    @property
    # @abstractmethod
    def run(self) -> Run:
        """The underlying GEMD run."""
        return self._run

    @property
    def assets(self) -> list:
        _assets = []
        if self.__class__.__name__ == "Ingredient":
            return [self.spec, self.run]
        else:
            _assets = [self.TEMPLATE, self.spec, self.run]
        return _assets

    def assert_linked(self, uuid_key="auto"):
        if (
            hasattr(self.spec, "template")
            and hasattr(self.spec.template, "uids")
            and (
                uuid_key in self.spec.template.uids.keys()
                and uuid_key in self.TEMPLATE.uids.keys()
            )
        ):
            if not self.spec.template.uids[uuid_key] == self.TEMPLATE.uids[uuid_key]:
                print(
                    f"spec's template is not linked to template by uuid key: {uuid_key}"
                )
            else:
                print("template and spec are linked properly.")
        else:
            print(f"uuid key: {uuid_key} not found in either templates.")

        if uuid_key in self.run.spec.uids.keys() and uuid_key in self.spec.uids.keys():
            if not self.run.spec.uids[uuid_key] == self.spec.uids[uuid_key]:
                print(f"run's spec is not linked to spec by uuid key: {uuid_key}")
            else:
                print("run and spec are linked properly.")
        else:
            print(f"uuid key: {uuid_key} not found in either specs.")

    ############################

    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: IngredientSpec = None,
        run: IngredientRun = None,
    ) -> "Ingredient":
        """
        Instantiate a `Ingredient` from a spec or run with appropriate validation.

        Note that the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        """

        if run is not None:
            if spec is None:
                spec = run.spec
        else:  # already checked that both can't be none, so only one scenario left
            if spec is None:
                raise ValueError("At least one of spec or run must be given.")

        ingredient = cls(name, notes=notes)

        if spec is not None:
            if not isinstance(spec, IngredientSpec):
                raise TypeError("spec must be a IngredientSpec.")

            ingredient._spec = spec

            ingredient.spec.name = name
            ingredient.spec.notes = notes

        if run is not None:
            if not isinstance(run, IngredientRun):
                raise TypeError("run must be a IngredientRun.")

            ingredient._run = run

            ingredient.run.notes = notes
            ingredient.run.spec = ingredient.spec

        else:
            ingredient._run = make_instance(ingredient.spec)

        return ingredient
