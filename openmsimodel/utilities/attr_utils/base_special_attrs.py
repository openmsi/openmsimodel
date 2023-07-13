'''Base for special attribute classes.'''

from typing import ClassVar, Union
from abc import ABC, abstractmethod
import re

import numpy as np
import pandas as pd

from gemd.entity.template.attribute_template import AttributeTemplate
from gemd.entity.attribute.base_attribute import BaseAttribute
from gemd.entity.object.base_object import BaseObject

from .utils import AttrTypes

__all__ = ['BaseSpecialAttrs']

class BaseSpecialAttrs(ABC):
    '''
    Abstract class for classes that provide convenient interfaces to certain types
    of attributes attached to GEMD objects.
    '''

    RE: ClassVar[re.Pattern]

    @abstractmethod
    def concat(self, *args: pd.DataFrame) -> None:
        '''
        Concatenate new data.
        
        Indices in the new data are respected and will replace rows with
        identical indices in the existing data.
        '''

    @abstractmethod
    def remove(self, index: int) -> None:
        '''Remove a row from the attributes by index, then reindex.'''

    @abstractmethod
    def update_object(self) -> None:
        '''
        Update the ``<Object>Spec`` or ``<Object>Run`` used to initialize
        with the attributes.

        This is performed in-place on the existing <object> and will
        overwrite any attributes added after ``<SubClass>`` initialization.
        '''

    @classmethod
    @abstractmethod
    def object_from_file(cls, *args, **kwargs) -> tuple[BaseObject, BaseObject]:
        '''
        Create an empty ``<Object>Spec`` and filled ``<Object>Run`` from a delimited file.
        
        Add parameters to the method definition as needed, e.g. filename, url,
        template, etc.
        '''

    @classmethod
    @abstractmethod
    def _parse(cls, attrs: list[BaseAttribute]):
        '''
        Match each attribute's name with regular expression.

        Should return ``DataFrame``(s) as appropriate and a list of other
        ``BaseAttribute``s.
        '''

    @classmethod
    @abstractmethod
    def _add_attr_to_df(cls, *args, **kwargs) -> None:
        '''Given a matching attribute, add it to a ``DataFrame`` as appropriate.'''

    @classmethod
    @abstractmethod
    def _reindex_df(cls, *args: pd.DataFrame):
        '''Add in any missing integer indices and sort.'''

    @classmethod
    @abstractmethod
    def _reindex_all_dfs(self) -> None:
        '''Ensure that each ``DataFrame`` has the same (maximum) number of indices.'''

    @abstractmethod
    def _reindex_all_attrs(self) -> None:
        '''Rename all attributes according to where they are in their ``DataFrame``.'''

    @staticmethod
    def _extract_attrs_from_df(df: pd.DataFrame) -> list[BaseAttribute]:
        '''Return a list of attributes from a ``DataFrame``.'''

        return [attr for col in df for attr in col if not pd.isna(attr)]

    @classmethod
    @abstractmethod
    def _create_attrs_from_df(
        cls,
        df: pd.DataFrame,
        template_dict: dict[str, AttributeTemplate],
        attr_types: AttrTypes,
        columns: list[str],
        names: list[str],
        units: list[Union[str, None]],
        origins: list[str]
        ):
        '''Create attributes from the `df` values.'''
