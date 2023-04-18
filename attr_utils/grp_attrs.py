'''Support for group attributes.'''

from typing import TypeAlias, ClassVar, Union, Optional, Any
import re

import numpy as np
import pandas as pd

from gemd import (
    MeasurementTemplate, MeasurementSpec, MeasurementRun,
    MaterialRun, Condition, Parameter, Property, FileLink,
    NominalCategorical, EmpiricalFormula, NominalInteger, NominalReal
)
from gemd.entity.template.attribute_template import AttributeTemplate
from gemd.entity.attribute.base_attribute import BaseAttribute

from .base_special_attrs import BaseSpecialAttrs
from .utils import AttrTypes, attr_template_dict, generate_tags, generate_source

__all__ = ['GrpAttrs']

Measurement: TypeAlias = Union[MeasurementSpec, MeasurementRun]

class GrpAttrs(BaseSpecialAttrs):
    '''
    Represent a single measurement's group attributes as ``DataFrame``s of
    attributes.

    Each row of the ``DataFrame``s represents a group of attributes. Each column
    is an attribute name.
    '''

    GRP: ClassVar[str] = '_grp'
    RE: ClassVar[re.Pattern] = re.compile(f'^(.+){GRP}(\\d+)$')
    CAT_STR: ClassVar[str] = 'categorical'
    FORM_STR: ClassVar[str] = 'formula'

    def __init__(self, measurement: Measurement) -> None:
        '''
        Parse a measurement's group attributes and create ``DataFrame``s for the
        conditions, parameters, and properties.

        Group attributes are expected to be named as ``<base_name>_grp<group>``.

        Parameters
        ----------
        measurement: MeasurmentSpec or MeasurementRun
            Measurement containing appropriately-named group attributes.
        '''        

        self._measurement = measurement

        conditions_tuple = self._parse(measurement.conditions)
        self._grp_conds: pd.DataFrame = conditions_tuple[0]
        self._other_conds: list[Condition] = conditions_tuple[1]

        parameters_tuple = self._parse(measurement.parameters)
        self._grp_params: pd.DataFrame = parameters_tuple[0]
        self._other_params: list[Parameter] = parameters_tuple[1]

        self._grp_props: pd.DataFrame = pd.DataFrame()
        self._other_props: list[Property] = []

        if isinstance(measurement, MeasurementRun):
            properties_tuple = self._parse(measurement.properties)
            self._grp_props = properties_tuple[0]
            self._other_props = properties_tuple[1]

        self._reindex_all_dfs()

    @property
    def measurement(self) -> Measurement:
        '''The measurement containing these attributes.'''
        return self._measurement

    @property
    def group_conditions(self) -> pd.DataFrame:
        '''Conditions of groups.'''
        return self._grp_conds
    
    @property
    def other_conditions(self) -> list[Condition]:
        '''Non-group conditions.'''
        return self._other_conds

    @property
    def group_parameters(self) -> pd.DataFrame:
        '''Parameters of groups.'''
        return self._grp_params
    
    @property
    def other_parameters(self) -> list[Parameter]:
        '''Non-group parameters.'''
        return self._other_params

    @property
    def group_properties(self) -> pd.DataFrame:
        '''Properties of groups.'''
        return self._grp_props
    
    @property
    def other_properties(self) -> list[Property]:
        '''Non-group properties.'''
        return self._other_props

    def concat(self, df: pd.DataFrame) -> None:
        '''
        Concatenate group attribute data.

        Indices in the new data are respected and will replace rows with
        identical indices in the existing data.

        Parameters
        ----------
        df: DataFrame
            Should contain the appropriate attribute columns to update the
            groups.
        '''

        attrs = pd.concat(self._df_list(), axis=1)
        attrs = pd.concat((attrs, df), axis=0)
        attrs = attrs[~attrs.index.duplicated(keep='last')]

        self._grp_conds = attrs.loc[:, self._grp_conds.columns]
        self._grp_params = attrs.loc[:, self._grp_params.columns]
        self._grp_props = attrs.loc[:, self._grp_props.columns]

        self._reindex_all_dfs()
        self._reindex_all_attrs()

    def remove(self, index: int) -> None:
        '''Remove a row from the attributes by index, then reindex.'''

        new_index = np.arange(len(self._grp_conds)-1)

        for df in self._df_list():
            df.drop(index=index, inplace=True)
            df.index = new_index

        self._reindex_all_attrs()

    def update_object(self) -> None:
        '''
        Update the ``MeasurementSpec`` or ``MeasurmentRun`` used to initialize
        with the attributes.

        This is performed in-place on the existing measurement and will
        overwrite any attributes added after ``GrpAttrs`` initialization.
        '''

        grp_conds = self._extract_attrs_from_df(self._grp_conds)
        grp_params = self._extract_attrs_from_df(self._grp_params)

        self._measurement.conditions = self._other_conds + grp_conds
        self._measurement.parameters = self._other_params + grp_params

        if isinstance(self._measurement, MeasurementRun):
            grp_props = self._extract_attrs_from_df(self._grp_props)
            self._measurement.properties = self._other_props + grp_props

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
            The units of the attribute values. ``"categorical"`` for
            NominalCategorical, ``"formula"``, for EmpiricalFormula,
            other ``str`` for NominalReal, ``None`` for NominalInteger.
        origins: list[str]
            The origins of the attribute values.
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

        if not (len(attr_types) == len(columns) == len(names) == len(units) == len(origins)):
            raise ValueError('Iterable inputs must be equal in length.')

        conditions, parameters, properties = cls._create_attrs_from_df(
            df, template_dict, attr_types, columns, names, units, origins
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
    def _parse(cls, attrs: list[BaseAttribute]) -> tuple[pd.DataFrame, list[BaseAttribute]]:
        '''
        Match each attribute's name with regular expression.

        Base name determines the column. _grp value determines the row.
        '''

        grp_df = pd.DataFrame()
        other_attrs = []

        for attr in attrs:

            match = cls.RE.match(attr.name)

            if match is not None:
                cls._add_attr_to_df(attr, match, grp_df)
            else:
                other_attrs.append(attr)

        reindexed_df = cls._reindex_df(grp_df)

        return reindexed_df, other_attrs

    @classmethod
    def _add_attr_to_df(
        cls,
        attr: BaseAttribute,
        match: re.Match[str],
        grp_df: pd.DataFrame
        ) -> None:
        '''Given a matching attribute, add it to `grp_df`.'''

        # regular expression groups
        match_groups = match.groups()
        base_name = match_groups[0]
        grp_val = int(match_groups[1])
  
        # add column if not there
        if base_name not in grp_df.columns:
            grp_df[base_name] = np.nan

        # place attribute in appropriate df
        grp_df.loc[grp_val, base_name] = attr

    @classmethod
    def _reindex_df(cls, grp_df: pd.DataFrame) -> pd.DataFrame:
        '''Add in any missing integer indices and sort.'''

        if len(grp_df) > 0:
            grp_df = grp_df.reindex(np.arange(grp_df.index.max()+1))

        return grp_df

    def _reindex_all_dfs(self) -> None:
        '''Ensure that each ``DataFrame`` has the same (maximum) number of groups.'''

        if len(self._grp_conds) == len(self._grp_params):
            return

        grp_max = int(np.nanmax([self._grp_conds.index.max(), self._grp_params.index.max()]))

        self._grp_conds = self._grp_conds.reindex(np.arange(grp_max+1))
        self._grp_params = self._grp_params.reindex(np.arange(grp_max+1))
        self._grp_props = self._grp_props.reindex(np.arange(grp_max+1))

    def _df_list(self) -> list[pd.DataFrame]:
        '''Return a list of the attributes ``DataFrame``s.'''
        return [self._grp_conds, self._grp_params, self._grp_props]

    def _reindex_all_attrs(self) -> None:
        '''Rename all attributes according to where they are in their ``DataFrame``.'''

        for df in self._df_list():
            for name, series in df.items():
                for i, attr in series.items():
                    if not pd.isna(attr):
                        attr.name = f'{name}{self.GRP}{i}'

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

                if u == cls.CAT_STR:
                    value = NominalCategorical(val)
                elif u == cls.FORM_STR:
                    value = EmpiricalFormula(val)
                elif u is None:
                    value = NominalInteger(val)
                else:
                    value = NominalReal(val, u)

                to_append.append(a(
                    name=f'{n}{cls.GRP}{i}',
                    value=value,
                    template=template_dict[n],
                    origin=o
                ))

        return conditions, parameters, properties
