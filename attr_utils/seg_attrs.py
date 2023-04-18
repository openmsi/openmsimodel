'''Support for segment (ramp/hold) attributes.'''

from typing import TypeAlias, ClassVar, Union, Optional, Any
import re

import numpy as np
import pandas as pd

from gemd import (
    ProcessTemplate, ProcessSpec, ProcessRun, ParameterTemplate,
    Condition, Parameter, FileLink,
    NominalCategorical, EmpiricalFormula, NominalInteger, NominalReal
)
from gemd.entity.template.attribute_template import AttributeTemplate
from gemd.entity.attribute.base_attribute import BaseAttribute

from .base_special_attrs import BaseSpecialAttrs
from .utils import AttrTypes, attr_template_dict, generate_tags, generate_source

__all__ = ['SegAttrs']

Process: TypeAlias = Union[ProcessSpec, ProcessRun]

class SegAttrs(BaseSpecialAttrs):
    '''
    Represent a single process's segment (ramp/hold) attributes as
    ``DataFrame``s of attributes.

    Each row of the ``DataFrame``s represents a segment, in order. Each column
    is an attribute name. The special ``Segment type`` parameter must be one of
    the columns to indicate whether or not the segment is a ramp or hold
    segment.
    '''

    SEG: ClassVar[str] = '_seg'
    RE: ClassVar[re.Pattern] = re.compile(f'^(.+){SEG}(\\d+)$')
    SEG_PARAM_NAME: ClassVar[str] = 'Segment type'
    CAT_STR: ClassVar[str] = 'categorical'
    FORM_STR: ClassVar[str] = 'formula'

    def __init__(self, process: Process) -> None:
        '''
        Parse a process's segment attributes and create ``DataFrame``s for the
        conditions and parameters.

        Segment attributes are expected to be named as
        ``<base_name>_seg<segment>``.

        Parameters
        ----------
        process: ProcessSpec or ProcessRun
            Process containing appropriately-named segment attributes.
        '''        

        self._process = process

        conditions_tuple = self._parse(process.conditions)
        self._seg_conds: pd.DataFrame = conditions_tuple[0]
        self._other_conds: list[Condition] = conditions_tuple[1]

        parameters_tuple = self._parse(process.parameters)
        self._seg_params: pd.DataFrame = parameters_tuple[0]
        self._other_params: list[Parameter] = parameters_tuple[1]

        self._reindex_all_dfs()

    @property
    def process(self) -> Process:
        '''The process containing these attributes.'''
        return self._process

    @property
    def segment_conditions(self) -> pd.DataFrame:
        '''Conditions of ramp/hold segments.'''
        return self._seg_conds
    
    @property
    def other_conditions(self) -> list[Condition]:
        '''Non-segment conditions.'''
        return self._other_conds

    @property
    def segment_parameters(self) -> pd.DataFrame:
        '''Parameters of ramp/hold segments.'''
        return self._seg_params
    
    @property
    def other_parameters(self) -> list[Parameter]:
        '''Non-segment parameters.'''
        return self._other_params

    def concat(self, df: pd.DataFrame) -> None:
        '''
        Concatenate segment attribute data.

        Indices in the new data are respected and will replace rows with
        identical indices in the existing data.

        Parameters
        ----------
        df: DataFrame
            Should contain the appropriate attribute columns to update the
            segments.
        '''

        attrs = pd.concat(self._df_list(), axis=1)
        attrs = pd.concat((attrs, df), axis=0)
        attrs = attrs[~attrs.index.duplicated(keep='last')]

        self._seg_conds = attrs.loc[:, self._seg_conds.columns]
        self._seg_params = attrs.loc[:, self._seg_params.columns]

        self._reindex_all_dfs()
        self._reindex_all_attrs()

    def remove(self, index: int) -> None:
        '''Remove a row from the attributes by index, then reindex.'''

        new_index = np.arange(len(self._seg_conds)-1)

        for df in self._df_list():
            df.drop(index=index, inplace=True)
            df.index = new_index

        self._reindex_all_attrs()

    def update_object(self) -> None:
        '''
        Update the ``ProcessSpec`` or ``ProcessRun`` used to initialize
        with the attributes.

        This is performed in-place on the existing process and will
        overwrite any attributes added after ``SegAttrs`` initialization.
        '''

        seg_conds = self._extract_attrs_from_df(self._seg_conds)
        seg_params = self._extract_attrs_from_df(self._seg_params)

        self._process.conditions = self._other_conds + seg_conds
        self._process.parameters = self._other_params + seg_params

    @classmethod
    def object_from_file(
        cls,
        filename: str,
        url: str,
        process_template: ProcessTemplate,
        attr_types: AttrTypes,
        columns: list[str],
        names: list[str],
        units: list[Union[str, None]],
        origins: list[str],
        brand: Optional[str] = None,
        model: Optional[str] = None,
        instr_id: Optional[str] = None,
        email: Optional[str] = None,
        iso_date: Optional[str] = None,
        **read_csv_kwargs: Any
        ) -> tuple[ProcessSpec, ProcessRun]:
        '''
        Create an empty ``ProcessSpec`` and filled ``ProcessRun`` from a delimited file.

        One column must be the special ``"Segment type"`` column. The values in
        this column are expected to be ``"ramp"`` or ``"hold"``, indicating the
        segment type.

        Parameters
        ----------
        filename: str
            The name of the file.
        url: str
            The URL or file path leading to `filename`.
        process_template: ProcessTemplate
            The process template for this process. Must contain a
            ``ParameterTemplate`` with name ``"Segment type"``.
        attr_types: list of Type[Condition], Type[Parameter], Type[Property]
            The type of each attribute in the data, in order. The element
            corresponding to ``"Segment type"`` must be ``Parameter``.
        columns: list[str]
            The names of the data columns.
        names: list[str]
            The names of the attributes corresponding to an attribute in
            `process_template`. One must be ``"Segment type"``.
        units: list[str or None]
            The units of the attribute values. ``"categorical"`` for
            NominalCategorical, ``"formula"``, for EmpiricalFormula,
            other ``str`` for NominalReal, ``None`` for NominalInteger.
        origins: list[str]
            The origins of the attribute values.
        brand: str, optional
            The brand of the instrument used for the process.
        model: str, optional
            The model of the instrument used for the process.
            Ignored if `brand` is ``None``.
        instr_id: str, optional
            A further identifier for the instrument used, such as a number.
            Ignored if `brand` or `model` is ``None``.
        email: str, optional
            Email of the person who performed the process.
        iso_date: str, optional
            Date the process was performed, in ISO format.
        **read_csv_kwargs: Any
            Passed to ``pandas.read_csv()``.
        '''

        df = pd.read_csv(filename, **read_csv_kwargs)

        tags = generate_tags(brand, model, instr_id)

        source = generate_source(email, iso_date)

        template_dict = attr_template_dict(process_template)

        if not (len(attr_types) == len(columns) == len(names) == len(units) == len(origins)):
            raise ValueError('Iterable inputs must be equal in length.')

        # check for segment parameter template in process template
        if (
            cls.SEG_PARAM_NAME not in template_dict
            or not isinstance(template_dict[cls.SEG_PARAM_NAME], ParameterTemplate)
        ):
            raise ValueError(
                f'process_template must contain a ParameterTemplate named "{cls.SEG_PARAM_NAME}"'
            )

        # check for segment parameter in iterables
        if (
            cls.SEG_PARAM_NAME not in names
            or attr_types[names.index(cls.SEG_PARAM_NAME)] is not Parameter
            or units[names.index(cls.SEG_PARAM_NAME)] != cls.CAT_STR
        ):
            raise ValueError(
                f'names must contain "{cls.SEG_PARAM_NAME}" with corresponding '
                f'Type[Parameter] in attr_types and "{cls.CAT_STR}" in units.'
            )

        conditions, parameters = cls._create_attrs_from_df(
            df, template_dict, attr_types, columns, names, units, origins
        )

        spec = ProcessSpec(
            name=process_template.name,
            template=process_template,
            tags=tags
        )

        run = ProcessRun(
            name=process_template.name,
            spec=spec,
            tags=tags,
            source=source,
            conditions=conditions,
            parameters=parameters,
            file_links=[FileLink(filename=filename, url=url)]
        )

        return spec, run

    @classmethod
    def _parse(cls, attrs: list[BaseAttribute]) -> tuple[pd.DataFrame, list[BaseAttribute]]:
        '''
        Match each attribute's name with regular expression.

        Base name determines the column. _seg value determines the row.
        '''

        seg_df = pd.DataFrame()
        other_attrs = []

        for attr in attrs:

            match = cls.RE.match(attr.name)

            if match is not None:
                cls._add_attr_to_df(attr, match, seg_df)
            else:
                other_attrs.append(attr)

        reindexed_df = cls._reindex_df(seg_df)

        return reindexed_df, other_attrs

    @classmethod
    def _add_attr_to_df(
        cls,
        attr: BaseAttribute,
        match: re.Match[str],
        seg_df: pd.DataFrame
        ) -> None:
        '''Given a matching attribute, add it to `seg_df`.'''

        # regular expression groups
        match_groups = match.groups()
        base_name = match_groups[0]
        seg_val = int(match_groups[1])
  
        # add column if not there
        if base_name not in seg_df.columns:
            seg_df[base_name] = np.nan

        # place attribute in appropriate df
        seg_df.loc[seg_val, base_name] = attr

    @classmethod
    def _reindex_df(cls, seg_df: pd.DataFrame) -> pd.DataFrame:
        '''Add in any missing integer indices and sort.'''

        if len(seg_df) > 0:
            seg_df = seg_df.reindex(np.arange(seg_df.index.max()+1))

        return seg_df

    def _reindex_all_dfs(self) -> None:
        '''Ensure that each ``DataFrame`` has the same (maximum) number of segments.'''

        if len(self._seg_conds) == len(self._seg_params):
            return

        seg_max = int(np.nanmax([self._seg_conds.index.max(), self._seg_params.index.max()]))

        self._seg_conds = self._seg_conds.reindex(np.arange(seg_max+1))
        self._seg_params = self._seg_params.reindex(np.arange(seg_max+1))

    def _df_list(self) -> list[pd.DataFrame]:
        '''Return a list of the attributes ``DataFrame``s.'''
        return [self._seg_conds, self._seg_params]

    def _reindex_all_attrs(self) -> None:
        '''Rename all attributes according to where they are in their ``DataFrame``.'''

        for df in self._df_list():
            for name, series in df.items():
                for i, attr in series.items():
                    if not pd.isna(attr):
                        attr.name = f'{name}{self.SEG}{i}'

    @classmethod
    def _create_attrs_from_df(
        cls,
        df: pd.DataFrame,
        template_dict: dict[str, AttributeTemplate],
        attr_types: AttrTypes,
        columns: list[str],
        names: list[str],
        units: list[Union[str, None]],
        origins: list[str]
        ) -> tuple[list[Condition], list[Parameter]]:
        '''Create conditions and parameters from the `df` values.'''

        conditions = []
        parameters = []

        for a, c, n, u, o in zip(attr_types, columns, names, units, origins):

            if a is Condition:
                to_append = conditions
            elif a is Parameter:
                to_append = parameters
            else:
                raise ValueError(
                    'attr_types must consist of Type[Condition] or Type[Parameter], '
                    f'but found {type(a)}.'
                )

            for i, val in enumerate(df.loc[:, c]):

                if u == cls.CAT_STR:
                    value = NominalCategorical(val)
                elif u == cls.FORM_STR:
                    value = EmpiricalFormula(val)
                elif u is None:
                    value = NominalInteger(val)
                else:
                    value = NominalReal(val, u)

                to_append.append(a(
                    name=f'{n}{cls.SEG}{i}',
                    value=value,
                    template=template_dict[n],
                    origin=o
                ))

        return conditions, parameters
