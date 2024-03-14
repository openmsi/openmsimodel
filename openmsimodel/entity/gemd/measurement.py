"""Base class for measurements."""

from typing import ClassVar, Optional

from gemd import (
    MeasurementTemplate,
    MeasurementSpec,
    MeasurementRun,
    MaterialRun,
    Condition,
    Parameter,
    Property,
)
from gemd.entity.util import make_instance

from openmsimodel.entity.gemd.process_or_measurement import ProcessOrMeasurement


class Measurement(ProcessOrMeasurement):
    """
    Base element for measurements.

    """

    _TempType = MeasurementTemplate
    _SpecType = MeasurementSpec
    _RunType = MeasurementRun

    TEMPLATE: ClassVar[MeasurementTemplate]

    def __init__(
        self,
        name: str,
        *,
        template: MeasurementTemplate = None,
        notes: Optional[str] = None,
        conditions: Optional[list[Condition]] = None,
        parameters: Optional[list[Parameter]] = None,
        properties: Optional[list[Property]] = None,
        material: Optional[MaterialRun] = None
    ) -> None:
        super().__init__(
            name,
            template=template,
            notes=notes,
            conditions=conditions,
            parameters=parameters,
        )

        if properties is None:
            properties = []

        self.update_properties(*properties, replace_all=True)

        self.set_material(material)

    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: MeasurementSpec = None,
        run: MeasurementRun = None
    ) -> "Measurement":
        """
        Instantiate a `Measurement` from a spec or run with appropriate validation.

        Note that the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        """
        if run is not None:
            if spec is None:
                spec = run.spec
        else:
            if spec is None:
                raise ValueError("At least one of spec or run must be given.")
        template = spec.template

        measurement = cls(name, notes=notes, template=template)

        if spec is not None:
            if not isinstance(spec, MeasurementSpec):
                raise TypeError("spec must be a MeasurementSpec.")

            measurement._spec = spec

            measurement.spec.name = name
            measurement.spec.notes = notes

            measurement.update_conditions(which="spec")
            measurement.update_parameters(which="spec")

        if run is not None:
            if not isinstance(run, MeasurementRun):
                raise TypeError("run must be a MeasurementRun.")

            measurement._run = run

            measurement.run.name = name
            measurement.run.notes = notes
            measurement.run.spec = measurement.spec

            measurement.update_conditions(which="run")
            measurement.update_parameters(which="run")
            measurement.update_properties(which="run")

            source = measurement.get_source()
            if source:
                measurement.set_source(
                    email=source["performed_by"], iso_date=source["performed_date"]
                )

        else:
            measurement._run = make_instance(measurement.spec)

        return measurement

    def get_material(self) -> str:
        """
        Get the name of the material on sstate the measurement run was performed.


        """

        return self._run.material.name

    def set_material(self, material: Optional[MaterialRun]) -> None:
        """
        Set the material on sstate the measurement run was performed.

        :param material: {MaterialRun, None}
            The measurement's material.
        """

        self._run.material = material

    @staticmethod
    def _prop_dict(run_props: list[Property]):
        """Return a ``dict`` of measurement run properties."""

        prop_dict = {
            prop.name: {"value": prop.value.as_dict(), "origin": prop.origin}
            for prop in run_props
        }

        return prop_dict
