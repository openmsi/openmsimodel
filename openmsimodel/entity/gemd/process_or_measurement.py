"""Base class for processes and measurement."""

from typing import ClassVar, Type, Union, Optional
import re
from datetime import datetime

from gemd import (
    ProcessTemplate,
    ProcessSpec,
    ProcessRun,
    MeasurementTemplate,
    MeasurementSpec,
    MeasurementRun,
    Condition,
    Parameter,
    PerformedSource,
)

from openmsimodel.entity.gemd.gemd_element import GEMDElement
from openmsimodel.utilities.typing import SpecOrRunLiteral
from openmsimodel.utilities.attributes import finalize_template


class ProcessOrMeasurement(GEMDElement):
    """Base class for processes and measurements."""

    _TempType: ClassVar[Type[Union[ProcessTemplate, MeasurementTemplate]]]
    _SpecType: ClassVar[Type[Union[ProcessSpec, MeasurementSpec]]]
    _RunType: ClassVar[Type[Union[ProcessRun, MeasurementRun]]]

    TEMPLATE: ClassVar[Union[ProcessTemplate, MeasurementTemplate]]

    INSTRUMENTS: ClassVar[dict[str, dict[str, tuple]]]

    # TODO: measurement specs dont take properties but runs do
    def __init__(
        self,
        name: str,
        *,
        template: ClassVar[Union[ProcessTemplate, MeasurementTemplate]] = None,
        notes: Optional[str] = None,
        conditions: Optional[list[Condition]] = None,
        parameters: Optional[list[Parameter]] = None,
        which: SpecOrRunLiteral = "spec",  # TODO: fix this
    ) -> None:
        super().__init__(name, template=template, notes=notes)

        if conditions is None:
            conditions = []

        if parameters is None:
            parameters = []

        # FIXME: would this work if template?
        self.update_conditions(
            *conditions, replace_all=True, which=which
        )  # TODO change which? or add param?

        self.update_parameters(*parameters, replace_all=True, which=which)

    ############################### CONDITIONS ###############################

    def update_conditions(
        self,
        *conditions: Condition,
        replace_all: bool = False,
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """
        Change or add conditions.

        Parameters
        ----------
        *conditions: Condition
            The conditions to change (by name) or add.
        replace_all: bool, default False
            If ``True``, remove any existing conditions before adding new ones.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to update the spec, run, or both.

        Raises
        ------
        ValueError
            If the name of a condition is not supported.
        """

        self.update_attributes(
            AttrType=Condition,
            attributes=conditions,
            replace_all=replace_all,
            which=which,
        )

    def remove_conditions(
        self, *condition_names: str, which: SpecOrRunLiteral = "spec"
    ) -> None:
        """
        Remove conditions by name.

        *condition_names: str
            The names of conditions to remove.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to remove from the spec, run, or both.

        Raises
        ------
        ValueError
            If the name of a condition is not supported.
        """

        self.remove_attributes(
            AttrType=Condition, attr_names=condition_names, which=which
        )

    def get_conditions_dict(self):
        """Return a ``dict`` of the spec and run conditions."""
        return self._spec_run_dict(self._spec.conditions, self._run.conditions)

    ############################### PARAMETERS ###############################

    def update_parameters(
        self,
        *parameters: Parameter,
        replace_all: bool = False,
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """
        Change or add parameters.

        Parameters
        ----------
        *parameters: Parameter
            The parameters to change (by name) or add.
        replace_all: bool, default False
            If ``True``, remove any existing parameters before adding new ones.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to update the spec, run, or both.

        Raises
        ------
        ValueError
            If the name of a parameter is not supported.
        """

        self.update_attributes(
            AttrType=Parameter,
            attributes=parameters,
            replace_all=replace_all,
            which=which,
        )

    def remove_parameters(
        self, *parameter_names: str, which: SpecOrRunLiteral = "spec"
    ) -> None:
        """
        Remove parameters by name.

        *parameter_names: str
            The names of parameters to remove.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to remove from the spec, run, or both.

        Raises
        ------
        ValueError
            If the name of a parameter is not supported.
        """

        self.remove_attributes(
            AttrType=Parameter, attr_names=parameter_names, which=which
        )

    def get_parameters_dict(self):
        """Return a ``dict`` of the spec and run parameters."""
        return self._spec_run_dict(self._spec.parameters, self._run.parameters)

    def get_source(self) -> dict[str, str]:
        """
        Get the run's source.

        Returns
        -------
        source: dict
            ``{'performed_by': '<email>', 'performed_date': '<iso_date>'}``
        """
        if not self._run.source:
            return
        run_source = self._run.source.as_dict()

        return {
            "performed_by": run_source["performed_by"],
            "performed_date": run_source["performed_date"],
        }

    def set_source(self, email: str, iso_date: Optional[str] = None) -> None:
        """
        Set the run's source with a valid email address and an optional ISO date string.

        Parameters
        ----------
        email: str
            A valid email address.
        date: str, optional
            A date string to be passed to ``datetime.fromisoformat``.

        Raises
        ------
        ValueError
            If `email` is invalid.
        """

        if iso_date is not None:
            iso_date = datetime.fromisoformat(iso_date).isoformat(timespec="auto")

        self._run.source = PerformedSource(email, iso_date)

    # TODO: Move this to base node?
    @staticmethod
    def _spec_run_dict(
        spec_attrs: Union[list[Condition], list[Parameter]],
        run_attrs: Union[list[Condition], list[Parameter]],
    ):
        """
        Return a ``dict`` of spec and run conditions or parameters.

        The keys are the names of the spec and run attributes.
        Each value is a ``dict`` with the keys ``'spec'`` and ``'run'``.
        Each ``'spec'`` and ``'run'`` key corresponds to another ``dict`` containing
        a value ``dict`` and origin ``str``, or ``None`` if the attribute is only
        found under one of spec or run.

        Example output:

        {
            'Duration': {
                'spec': {
                    'value': {
                        'nominal': 60,
                        'units': 'minutes',
                        'type': 'nominal_real'
                    },
                    'origin': 'specified'
                },
                'run': {
                    'value': None,
                    'origin': None
                }
            }
        }
        """

        spec_dict = {
            attr.name: {"value": attr.value.as_dict(), "origin": attr.origin}
            for attr in spec_attrs
        }
        run_dict = {
            attr.name: {"value": attr.value.as_dict(), "origin": attr.origin}
            for attr in run_attrs
        }

        attrs = {}

        for name, value_and_origin in spec_dict.items():
            attrs[name] = {"spec": value_and_origin, "run": None}

        for name, value_and_origin in run_dict.items():
            if name in attrs:
                attrs[name]["run"] = value_and_origin
            else:
                attrs[name] = {"spec": None, "run": value_and_origin}

        return attrs
