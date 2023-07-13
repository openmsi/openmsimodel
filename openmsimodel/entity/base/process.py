'''Base class for processes.'''

from typing import ClassVar, Optional

from gemd import ProcessTemplate, ProcessSpec, ProcessRun
from gemd.entity.util import make_instance

from .process_or_measurement import ProcessOrMeasurement

__all__ = ['Process']

class Process(ProcessOrMeasurement):
    '''
    Base class for processes.

    TODO: instructions for subclassing
    '''

    _TempType = ProcessTemplate
    _SpecType = ProcessSpec
    _RunType = ProcessRun

    TEMPLATE: ClassVar[ProcessTemplate] 

    @property
    def spec(self) -> ProcessSpec:
        '''The underlying process spec.'''
        return self._spec

    @property
    def run(self) -> ProcessRun:
        '''The underlying process run.'''
        return self._run
    
    @classmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: ProcessSpec = None,
        run: ProcessRun = None
        ) -> 'Process':
        '''
        Instantiate a `Process` from a spec or run with appropriate validation.

        Note that the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        '''

        if spec is None and run is None:
            raise ValueError('At least one of spec or run must be given.')

        process = cls(name, notes=notes)

        if spec is not None:

            if not isinstance(spec, ProcessSpec):
                raise TypeError('spec must be a ProcessSpec.')
            
            print(process.spec)
            process._spec = spec

            process.spec.name = name
            process.spec.notes = notes
            process.spec.template = cls.TEMPLATE

            process.update_conditions(which='spec')
            process.update_parameters(which='spec')

        if run is not None:

            if not isinstance(run, ProcessRun):
                raise TypeError('run must be a ProcessRun.')

            process._run = run

            process.run.name = name
            process.run.notes = notes
            process.run.spec = process.spec

            process.update_conditions(which='run')
            process.update_parameters(which='run')

            source = process.get_source()
            process.set_source(email=source['performed_by'], iso_date=source['performed_date'])

        else:
            process.run = make_instance(process.spec)

        return process

    def to_form(self) -> str:
        pass
