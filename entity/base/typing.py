'''Commonly-used types.'''

from typing import TypedDict, Union, Optional, Literal, Any
from typing_extensions import TypeAlias
from gemd import (
    MaterialTemplate, ProcessTemplate, MeasurementTemplate,
    MaterialSpec, ProcessSpec, MeasurementSpec,
    MaterialRun, ProcessRun, MeasurementRun
)
from gemd.enumeration import Origin

Temp: TypeAlias = Union[MaterialTemplate, ProcessTemplate, MeasurementTemplate]

Spec: TypeAlias = Union[MaterialSpec, ProcessSpec, MeasurementSpec]

Run: TypeAlias = Union[MaterialRun, ProcessRun, MeasurementRun]

SpecOrRun: TypeAlias = Union[Spec, Run]

SpecRunLiteral: TypeAlias = Literal['spec', 'run', 'both']

class TagsDict(TypedDict):
    '''Define dictionary representation of hierarchical tags.'''

    spec: dict[str, dict]
    run: dict[str, dict]

class FileLinksDict(TypedDict):
    '''Define dictionary containing file link strings for spec and run.'''

    spec: tuple[str, ...]
    run: tuple[str, ...]

class ProcessDict(TypedDict):
    '''Define dictionary containing process string for the spec and run.'''

    spec: str
    run: str

class ValueAndOrigin(TypedDict):
    '''Attribute value and origin as a dictionary.'''

    value: dict[str, Any]
    origin: Origin

class PropsAndCondsDict(TypedDict):
    '''Define dictionary output for material spec properties and conditions.'''

    property: ValueAndOrigin
    conditions: dict[str, ValueAndOrigin]

class ValueOriginDict(TypedDict):
    '''Define dictionary output for process and measurement spec/run conditions/parameters.'''

    spec: Optional[ValueAndOrigin]
    run: Optional[ValueAndOrigin]
