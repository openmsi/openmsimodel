from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.entity.gemd.measurement import Measurement

from typing import ClassVar, Type, Optional

from openmsimodel.utilities.typing import (
    Spec,
    Run,
)


def from_spec_or_run(
    name: str,
    *,
    notes: Optional[str] = None,
    spec: Spec = None,
    run: Run = None,
) -> "Element":
    """
    Instantiate a `Element` from a spec or run with appropriate validation.

    Note that the spec's and run's name and notes will be set to `name` and
    `notes`, the spec's template will be set to the class template,
    and the run's spec will be set to this spec.
    """
    if spec is None and run is None:
        raise ValueError("At least one of spec or run must be given.")

    if (spec is not None and spec.typ.startswith("material")) or (
        run is not None and run.typ.startswith("material")
    ):
        return Material.from_spec_or_run(name=name, notes=notes, spec=spec, run=run)
    elif (spec is not None and spec.typ.startswith("process")) or (
        run is not None and run.typ.startswith("process")
    ):
        return Process.from_spec_or_run(name=name, notes=notes, spec=spec, run=run)
    elif (spec is not None and spec.typ.startswith("measurement")) or (
        run is not None and run.typ.startswith("measurement")
    ):
        return Measurement.from_spec_or_run(name=name, notes=notes, spec=spec, run=run)
    elif (spec is not None and spec.typ.startswith("ingredient")) or (
        run is not None and run.typ.startswith("ingredient")
    ):
        return Ingredient.from_spec_or_run(name=name, notes=notes, spec=spec, run=run)
