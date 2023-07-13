'''Support for array attributes.'''

from typing import TypeAlias, ClassVar, Union, Optional, Any
import re

import numpy as np
import pandas as pd

from gemd import (
    MeasurementTemplate, MeasurementSpec, MeasurementRun, MaterialRun,
    Condition, Parameter, Property, NominalInteger, NominalReal, FileLink
)
from gemd.entity.template.attribute_template import AttributeTemplate
from gemd.entity.attribute.base_attribute import BaseAttribute

from .base_special_attrs import BaseSpecialAttrs
from .utils import AttrTypes, attr_template_dict, generate_tags, generate_source

__all__ = ['ArrAttrs']

Measurement: TypeAlias = Union[MeasurementSpec, MeasurementRun]

class ArrAttrs(BaseSpecialAttrs):
    '''
    Represent a single measurement's array attributes as ``DataFrame``s of attributes.

    Supports multiple arrays, each potentially with single attributes that
    apply to the entire array and indexed attributes with multiple values.

    If there are multiple arrays, each array must have the same attributes
    and the same length.
    '''

    ARR: ClassVar[str] = '_arr'
    IDX: ClassVar[str] = '_idx'
    RE: ClassVar[re.Pattern] = re.compile(f'^(.+){ARR}(\\d+)(?:{IDX}(\\d+))?$')

    def __init__(self, measurement: Measurement) -> None:
        '''
        Parse a measurement's array attributes and create ``DataFrame``s
        for the conditions, parameters, and properties.

        Array attributes are expected to be named as ``<base_name>_arr<array>``
        or ``<base_name>_arr<array>_idx<index>``.

        Parameters
        ----------
        measurement: MeasurementSpec or MeasurementRun
            Measurement containing appropriately-named array attributes.
        '''        

        self._measurement = measurement

        # single_attributes are those with only _arr
        # multiple_attributes are those with both _arr and _idx

        conditions_tuple = self._parse(measurement.conditions)
        self._single_conds: pd.DataFrame = conditions_tuple[0]
        self._multiple_conds: pd.DataFrame = conditions_tuple[1]
        self._other_conds: list[Condition] = conditions_tuple[2]

        parameters_tuple = self._parse(measurement.parameters)
        self._single_params: pd.DataFrame = parameters_tuple[0]
        self._multiple_params: pd.DataFrame = parameters_tuple[1]
        self._other_params: list[Parameter] = parameters_tuple[2]

        self._single_props: pd.DataFrame = pd.DataFrame()
        self._multiple_props: pd.DataFrame = pd.DataFrame()
        self._other_props: list[Property] = []

        if isinstance(measurement, MeasurementRun):
            properties_tuple = self._parse(measurement.properties)
            self._single_props = properties_tuple[0]
            self._multiple_props = properties_tuple[1]
            self._other_props = properties_tuple[2]

        self._reindex_all_dfs()

    @property
    def measurement(self) -> Measurement:
        '''The measurement containing these attributes.'''
        return self._measurement

    @property
    def single_conditions(self) -> pd.DataFrame:
        '''Conditions that apply to entire arrays.'''
        return self._single_conds.copy()

    @property
    def multiple_conditions(self) -> pd.DataFrame:
        '''Conditions with multiple values per array.'''
        return self._multiple_conds.copy()

    @property
    def other_conditions(self) -> list[Condition]:
        '''Non-array conditions.'''
        return self._other_conds.copy()

    @property
    def single_parameters(self) -> pd.DataFrame:
        '''Parameters that apply to entire arrays.'''
        return self._single_params.copy()

    @property
    def multiple_parameters(self) -> pd.DataFrame:
        '''Parameters with multiple values per array.'''
        return self._multiple_params.copy()

    @property
    def other_parameters(self) -> list[Parameter]:
        '''Non-array parameters.'''
        return self._other_params.copy()

    @property
    def single_properties(self) -> pd.DataFrame:
        '''Properties that apply to entire arrays.'''
        return self._single_props.copy()

    @property
    def multiple_properties(self) -> pd.DataFrame:
        '''Properties with multiple values per array.'''
        return self._multiple_props.copy()

    @property
    def other_properties(self) -> list[Property]:
        '''Non-array properties.'''
        return self._other_props.copy()

    def concat(
        self,
        single_df: Optional[pd.DataFrame] = None,
        multiple_df: Optional[pd.DataFrame] = None
        ) -> None:
        '''
        Concatenate data with the single and/or multiple attributes.

        Indices in the new data are respected and will replace rows with
        identical indices in the existing data.

        Parameters
        ----------
        single_df, multiple_df: DataFrame, optional
            Should contain the appropriate attribute columns to update the
            single attributes and multiple attributes, respectively.
            At least one of these must be provided.
        '''

        if single_df is None and multiple_df is None:
            raise ValueError('At least on of single_df and multiple_df must not be None.')
        
        if single_df is not None:

            single_attrs = pd.concat(self._single_df_list(), axis=1)
            single_attrs = pd.concat((single_attrs, single_df), axis=0)
            single_attrs = single_attrs[~single_attrs.index.duplicated(keep='last')]

            self._single_conds = single_attrs.loc[:, self._single_conds.columns]
            self._single_params = single_attrs.loc[:, self._single_params.columns]
            self._single_props = single_attrs.loc[:, self._single_props.columns]

        if multiple_df is not None:

            multiple_attrs = pd.concat(self._multiple_df_list(), axis=1)
            multiple_attrs = pd.concat((multiple_attrs, multiple_df), axis=0,)
            multiple_attrs = multiple_attrs[~multiple_attrs.index.duplicated(keep='last')]

            self._multiple_conds = multiple_attrs.loc[:, self._multiple_conds.columns]
            self._multiple_params = multiple_attrs.loc[:, self._multiple_params.columns]
            self._multiple_props = multiple_attrs.loc[:, self._multiple_props.columns]

        self._reindex_all_dfs()
        self._reindex_all_attrs()

    def remove(self, index: int) -> None:
        '''Remove a row from the attributes by index, then reindex.'''

        new_index = np.arange(len(self._single_conds)-1)

        for df in self._single_df_list():
            df.drop(index=index, inplace=True)
            df.index = new_index

        for df in self._multiple_df_list():
            df.drop(index=index, inplace=True)
            new_codes = np.array(df.index.codes)
            new_codes[0][new_codes[0] > index] -= 1
            df.index = pd.MultiIndex.from_arrays(new_codes)

        self._reindex_all_attrs()

    def update_object(self) -> None:
        '''
        Update the ``MeasurementSpec`` or ``MeasurementRun`` used to initialize
        with the attributes.

        This is performed in-place on the existing measurement and will
        overwrite any attributes added after ``ArrAttrs`` initialization.
        '''

        single_conds = self._extract_attrs_from_df(self._single_conds)
        multiple_conds = self._extract_attrs_from_df(self._multiple_conds)
        single_params = self._extract_attrs_from_df(self._single_params)
        multiple_params = self._extract_attrs_from_df(self._multiple_params)

        self._measurement.conditions = self._other_conds + single_conds + multiple_conds
        self._measurement.parameters = self._other_params + single_params + multiple_params

        if isinstance(self._measurement, MeasurementRun):
            single_props = self._extract_attrs_from_df(self._single_props)
            multiple_props = self._extract_attrs_from_df(self._multiple_props)
            self._measurement.properties = self._other_props + single_props + multiple_props

    @classmethod
    def object_from_file(
        cls,
        filename: str,
        url: str,
        material_run: MaterialRun,
        measurement_template: MeasurementTemplate,
        attr_types: AttrTypes,
        columns: list[str],
        names: list[str],
        units: list[Union[str, None]],
        origins: list[str],
        arr_pos: int = 0,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        instr_id: Optional[str] = None,
        email: Optional[str] = None,
        iso_date: Optional[str] = None,
        **read_csv_kwargs: Any
        ) -> tuple[MeasurementSpec, MeasurementRun]:
        '''
        Create an empty ``MeasurementSpec`` and filled ``MeasurementRun`` from a delimited file.

        Parameters
        ----------
        filename: str
            The name of the file.
        url: str
            The URL or file path leading to `filename`.
        material_run: str
            The relevant ``MaterialRun``.
        measurement_template: MeasurementTemplate
            The measurement template for this measurement.
        attr_types: list of Type[Condition], Type[Parameter], Type[Property]
            The type of each attribute in the data, in order.
        columns: list[str]
            The names of the data columns.
        names: list[str]
            The names of the attributes corresponding to an attribute in `measurement_template`.
        units: list[str or None]
            The units of the attribute values. str for NominalReal, None for NominalInteger.
        origins: list[str]
            The origins of the attribute values.
        arr_pos: int, default 0
            The integer array position to use in the generated attribute names.
        brand: str, optional
            The brand of the instrument used for the measurement.
        model: str, optional
            The model of the instrument used for the measurement.
            Ignored if `brand` is ``None``.
        instr_id: str, optional
            A further identifier for the instrument used, such as a number.
            Ignored if `brand` or `model` is ``None``.
        email: str, optional
            Email of the person who performed the measurement.
        iso_date: str, optional
            Date the measurement was performed, in ISO format.
        **read_csv_kwargs: Any
            Passed to ``pandas.read_csv()``.
        '''

        df = pd.read_csv(filename, **read_csv_kwargs)

        tags = generate_tags(brand, model, instr_id)

        source = generate_source(email, iso_date)

        template_dict = attr_template_dict(measurement_template)

        arr_pos = int(arr_pos)
        if arr_pos < 0:
            raise ValueError('arr_pos must be a non-negative integer.')

        if not (len(attr_types) == len(columns) == len(names) == len(units) == len(origins)):
            raise ValueError('Iterable inputs must be equal in length.')

        conditions, parameters, properties = cls._create_attrs_from_df(
            df, template_dict, attr_types, columns, names, units, origins, arr_pos
        )

        spec = MeasurementSpec(
            name=measurement_template.name,
            template=measurement_template,
            tags=tags
        )

        run = MeasurementRun(
            name=measurement_template.name,
            spec=spec,
            tags=tags,
            material=material_run,
            source=source,
            conditions=conditions,
            parameters=parameters,
            properties=properties,
            file_links=[FileLink(filename=filename, url=url)]
        )

        return spec, run

    @classmethod
    def _parse(
        cls,
        attrs: list[BaseAttribute]
        ) -> tuple[pd.DataFrame, pd.DataFrame, list[BaseAttribute]]:
        '''
        Match each attribute's name with regular expression.

        Base name determines the column. For single attributes (_arr only),
        value determines the row. For multiple attributes (_arr and _idx),
        array value determines the first row level in the row ``MultiIndex``
        and index value determines the second row level.
        '''

        single_df = pd.DataFrame()
        multiple_df = pd.DataFrame(index=pd.MultiIndex.from_arrays([[],[]]))
        other_attrs = []

        for attr in attrs:

            match = cls.RE.match(attr.name)

            if match is not None:
                cls._add_attr_to_df(attr, match, single_df, multiple_df)
            else:
                other_attrs.append(attr)

        reindexed_dfs = cls._reindex_df(single_df, multiple_df)

        return (*reindexed_dfs, other_attrs)

    @classmethod
    def _add_attr_to_df(
        cls,
        attr: BaseAttribute,
        match: re.Match[str],
        single_df: pd.DataFrame,
        multiple_df: pd.DataFrame
        ) -> None:
        '''Given a matching attribute, add it to `single_df` or `multiple_df` as appropriate.'''

        # regular expression groups
        match_groups = match.groups()
        base_name = match_groups[0]
        arr = int(match_groups[1])

        # _arr<array> case
        if match_groups[2] is None:
            df = single_df
            row_pos = arr
        # _arr<array>_idx<index> case
        else:
            df = multiple_df
            row_pos = (arr, int(match_groups[2]))
  
        # add column if not there
        if base_name not in df.columns:
            df[base_name] = np.nan

        # place attribute in appropriate df
        df.loc[row_pos, base_name] = attr

    @classmethod
    def _reindex_df(
        cls,
        single_df: pd.DataFrame,
        multiple_df: pd.DataFrame
        ) -> tuple[pd.DataFrame, pd.DataFrame]:
        '''Add in any missing integer indices and sort.'''

        # determine maximum arr from both dfs and maximum idx
        if len(single_df) > 0 and len(multiple_df) > 0:
            arr_max = max(single_df.index.max(), multiple_df.index.levels[0].max())
            idx_max = multiple_df.index.levels[1].max()
        elif len(single_df) > 0:
            arr_max = single_df.index.max()
        elif len(multiple_df) > 0:
            arr_max = multiple_df.index.levels[0].max()
            idx_max = multiple_df.index.levels[1].max()

        if len(single_df) > 0:
            single_df = single_df.reindex(np.arange(arr_max+1))

        if len(multiple_df) > 0:
            multiple_df = multiple_df.reindex(
                pd.MultiIndex.from_product((np.arange(arr_max+1), np.arange(idx_max+1)))
            )

        return single_df, multiple_df

    def _reindex_all_dfs(self) -> None:
        '''Ensure that each ``DataFrame`` has the same (maximum) number of arrays.'''

        if (
            len(self._single_conds) == len(self._single_params) == len(self._single_props) == 
            len(self._multiple_conds) == len(self._multiple_params) == len(self._multiple_props)==0
        ):
            return

        arr_max = int(np.nanmax([
            self._single_conds.index.max(),
            self._single_params.index.max(),
            self._single_props.index.max()
        ]))

        self._single_conds = self._single_conds.reindex(np.arange(arr_max+1))
        self._single_params = self._single_params.reindex(np.arange(arr_max+1))
        self._single_props = self._single_props.reindex(np.arange(arr_max+1))
        
        if len(self._multiple_conds) == len(self._multiple_params) == len(self._multiple_props)==0:
            return

        idx_max = 0
        
        if len(self._multiple_conds) > 0:
            idx_max = max(idx_max, self._multiple_conds.index.levels[1].max())

        if len(self._multiple_params) > 0:
            idx_max = max(idx_max, self._multiple_params.index.levels[1].max())

        if len(self._multiple_props) > 0:
            idx_max = max(idx_max, self._multiple_props.index.levels[1].max())

        self._multiple_conds = self._multiple_conds.reindex(
            pd.MultiIndex.from_product((np.arange(arr_max+1), np.arange(idx_max+1)))
        )
        self._multiple_params = self._multiple_params.reindex(
            pd.MultiIndex.from_product((np.arange(arr_max+1), np.arange(idx_max+1)))
        )
        self._multiple_props = self._multiple_props.reindex(
            pd.MultiIndex.from_product((np.arange(arr_max+1), np.arange(idx_max+1)))
        )

        idx_row_maxes=[
            max(
                self._multiple_conds.loc[arr_val, :].last_valid_index() or 0,
                self._multiple_params.loc[arr_val, :].last_valid_index() or 0,
                self._multiple_props.loc[arr_val, :].last_valid_index() or 0,
            )
            for arr_val in range(arr_max+1)
        ]

        to_drop = [(arr_val, idx_row_max) for i, arr_val in enumerate(range(arr_max+1)) for idx_row_max in range(idx_row_maxes[i]+1, idx_max+1)]

        self._multiple_conds.drop(index=to_drop, inplace=True)
        self._multiple_params.drop(index=to_drop, inplace=True)
        self._multiple_props.drop(index=to_drop, inplace=True)

    def _single_df_list(self) -> list[pd.DataFrame]:
        '''Return a list of the single attributes ``DataFrame``s.'''
        return [self._single_conds, self._single_params, self._single_props]

    def _multiple_df_list(self) -> list[pd.DataFrame]:
        '''Return a list of the multiple attributes ``DataFrame``s.'''
        return [self._multiple_conds, self._multiple_params, self._multiple_props]

    def _reindex_all_attrs(self) -> None:
        '''Rename all attributes according to where they are in their ``DataFrame``.'''

        for df in self._single_df_list():
            for name, series in df.items():
                for i, attr in series.items():
                    if not pd.isna(attr):
                        attr.name = f'{name}{self.ARR}{i}'

        for df in self._multiple_df_list():
            for name, series in df.items():
                for i, attr in series.items():
                    if not pd.isna(attr):
                        attr.name = f'{name}{self.ARR}{i[0]}{self.IDX}{i[1]}'

    @classmethod
    def _create_attrs_from_df(
        cls,
        df: pd.DataFrame,
        template_dict: dict[str, AttributeTemplate],
        attr_types: AttrTypes,
        columns: list[str],
        names: list[str],
        units: list[Union[str, None]],
        origins: list[str],
        arr_pos: int
        ) -> tuple[list[Condition], list[Parameter], list[Property]]:
        '''Create conditions, parameters, and properties from the `df` values.'''

        conditions = []
        parameters = []
        properties = []

        for a, c, n, u, o in zip(attr_types, columns, names, units, origins):
            if a is Condition:
                to_append = conditions
            elif a is Parameter:
                to_append = parameters
            elif a is Property:
                to_append = properties
            else:
                raise ValueError(
                    'attr_types must consist of Type[Condition], Type[Parameter], '
                    f'or Type[Property], but found {type(a)}.'
                )
            for i, val in enumerate(df.loc[:, c]):
                to_append.append(a(
                    name=f'{n}{cls.ARR}{arr_pos}{cls.IDX}{i}',
                    value=(NominalInteger(val) if u is None else NominalReal(val, u)),
                    template=template_dict[n],
                    origin=o
                ))

        return conditions, parameters, properties
