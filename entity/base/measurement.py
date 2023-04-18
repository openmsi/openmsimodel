'''Base class for measurements.'''

from typing import ClassVar, Optional

from gemd import (
    MeasurementTemplate, MeasurementSpec, MeasurementRun,
    MaterialRun, Condition, Parameter, Property
)
from gemd.entity.util import make_instance

from entity.base.typing import ValueAndOrigin

from .process_or_measurement import ProcessOrMeasurement

__all__ = ['Measurement']

class Measurement(ProcessOrMeasurement):
    '''
    Base class for measurements.

    TODO: instructions for subclassing
    '''

    _TempType = MeasurementTemplate
    _SpecType = MeasurementSpec
    _RunType = MeasurementRun

    TEMPLATE: ClassVar[MeasurementTemplate]

    def __init__(
        self,
        name: str,
        *,
        notes: Optional[str] = None,
        conditions: Optional[list[Condition]] = None,
        parameters: Optional[list[Parameter]] = None,
        properties: Optional[list[Property]] = None,
        material: Optional[MaterialRun] = None
        ) -> None:

        super().__init__(name, notes=notes, conditions=conditions, parameters=parameters)

        if properties is None:
            properties = []

        self.update_properties(properties=properties, replace_all=True)

        self.set_material(material)

    @property
    def spec(self) -> MeasurementSpec:
        '''The underlying measurement spec.'''
        return self._spec

    @property
    def run(self) -> MeasurementRun:
        '''The underlying measurement run.'''
        return self._run

    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: MeasurementSpec = None,
        run: MeasurementRun = None
        ) -> 'Measurement':
        '''
        Instantiate a `Measurement` from a spec or run with appropriate validation.

        Note that the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        '''

        if spec is None and run is None:
            raise ValueError('At least one of spec or run must be given.')

        measurement = cls(name, notes=notes)

        if spec is not None:

            if not isinstance(spec, MeasurementSpec):
                raise TypeError('spec must be a MeasurementSpec.')

            measurement.spec = spec

            measurement.spec.name = name
            measurement.spec.notes = notes
            measurement.spec.template = cls.TEMPLATE

            measurement.update_conditions(which='spec')
            measurement.update_parameters(which='spec')

        if run is not None:

            if not isinstance(run, MeasurementRun):
                raise TypeError('run must be a MeasurementRun.')

            measurement.run = run

            measurement.run.name = name
            measurement.run.notes = notes
            measurement.run.spec = measurement.spec

            measurement.update_conditions(which='run')
            measurement.update_parameters(which='run')
            measurement.update_properties()

            source = measurement.get_source()
            measurement.set_source(email=source['performed_by'], iso_date=source['performed_date'])

        else:
            measurement.run = make_instance(measurement.spec)

        return measurement

    def get_material(self) -> str:
        '''
        Get the name of the material on which the measurement run was performed.

        Returns
        -------
        material_name: str
        '''

        return self._run.material.name

    def set_material(self, material: Optional[MaterialRun]) -> None:
        '''
        Set the material on which the measurement run was performed.

        Parameters
        ----------
        material: {MaterialRun, None}
            The measurement's material.
        '''

        self._run.material = material

    def get_properties_dict(self) -> dict[str, ValueAndOrigin]:
        '''
        Return a ``dict`` of measurement run properties.

        The keys are the names of the properties.
        Each value is a ``dict`` containing a value ``dict`` and origin ``str``.

        Example output:

        {
            'Measured intensity': {
                'value': {'nominal': 1234, 'units': '', 'type': 'nominal_real'},
                'origin': 'measured'
            },
            'Background-subtracted intensity': {
                'value': {'nominal': 1000, 'units': '', 'type': 'nominal_real'},
                'origin': 'computed'
            },
        }
        '''

        return self._prop_dict(self._run.properties)

    def update_properties(self, properties: Property, replace_all: bool = False) -> None:
        '''
        Change or add measured properties of the measurement run.

        Parameters
        ----------
        *properties: Property
            The properties to change (by name) or add.
        replace_all: bool, default False
            If ``True``, remove any existing properties before adding new ones.

        Raises
        ------
        ValueError
            If the name of a property is not supported.
        '''

        self._update_attributes(
            AttrType=Property,
            attributes=properties,
            replace_all=replace_all,
            which='run'
        )

    def remove_properties(self, *property_names: str ) -> None:
        '''
        Remove measured properties from the measurement run by name.

        *property_names: str
            The names of properties to remove.

        Raises
        ------
        ValueError
            If the name of a property is not supported.
        '''

        self._remove_attributes(AttrType=Property, attr_names=property_names, which='run')

    @staticmethod
    def _prop_dict(run_props: list[Property]) -> dict[str, ValueAndOrigin]:
        '''Return a ``dict`` of measurement run properties.'''

        prop_dict = {
            prop.name: {
                'value': prop.value.as_dict(),
                'origin': prop.origin
            }
            for prop in run_props
        }

        return prop_dict

    def to_form(self) -> str:
        pass
