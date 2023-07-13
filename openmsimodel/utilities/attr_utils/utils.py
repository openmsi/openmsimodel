'''General attribute utilities.'''

from typing import TypeAlias, Type, Union, Optional
import re
from datetime import datetime

from gemd import Condition, Parameter, Property, PerformedSource
from gemd.entity.template.attribute_template import AttributeTemplate
from gemd.entity.template.base_template import BaseTemplate

AttrTypes: TypeAlias = list[Union[Type[Condition], Type[Parameter], Type[Property]]]

def attr_template_dict(template: BaseTemplate) -> dict[str, AttributeTemplate]:
    '''
    Create a dictionary mapping attribute template names to the attributes themselves.
    
    Parameters
    ----------
    template: BaseTemplate
        An object template containing the attribute templates.

    Returns
    -------
    template_dict: dict
        Mapping of attribute template names to attribute templates.
    '''

    attrs = []

    try:
        attrs.extend(template.conditions)
    except AttributeError:
        pass
    try:
        attrs.extend(template.parameters)
    except AttributeError:
        pass
    try:
        attrs.extend(template.properties)
    except AttributeError:
        pass

    template_dict = {}

    for attr_temp, bounds in attrs:
        # deal with more restrictive bounds
        if bounds is not None:
            restricted_temp = attr_temp.__class__.build(attr_temp.dump())
            restricted_temp.bounds = bounds
            template_dict[attr_temp.name] = restricted_temp
        else:
            template_dict[attr_temp.name] = attr_temp

    return template_dict

def generate_tags(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    instr_id: Optional[str] = None
    ) -> list[str]:
    '''Return a tags list containing one ``str`` from brand, model, and instrument id.'''

    tags = []

    if brand is not None:
        tag = str(brand)
        if model is not None:
            tag += f'::{model}'
            if instr_id is not None:
                tag += f'::{instr_id}'
        tags.append(tag)

    return tags

def generate_source(
    email: Optional[str] = None,
    iso_date: Optional[str] = None
    ) -> Optional[PerformedSource]:
    '''
    Generate a ``PerformedSource`` with a valid email address and an optional ISO date string.

    Parameters
    ----------
    email: str, optional
        A valid email address.
    date: str, optional
        A date string to be passed to ``datetime.fromisoformat``.

    Returns
    -------
    source: PerformedSource or None
        ``PerformedSource`` with email and date, or ``None`` if neither is supplied.

    Raises
    ------
    ValueError
        If `email` is invalid.
    '''

    if email is None and iso_date is None:
        return None

    if email is not None and not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
        raise ValueError(
            'Invalid email. Must contain a single "@" and at least one "." after the "@".'
        )

    if iso_date is not None:
        iso_date = datetime.fromisoformat(iso_date).isoformat(timespec='auto')

    return PerformedSource(email, iso_date)
