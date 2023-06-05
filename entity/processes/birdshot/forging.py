from typing import ClassVar

from gemd import ProcessTemplate

from entity.base import Process
from entity.base.attributes import AttrsDict, define_attribute, finalize_template

__all__ = ["Forging"]


class Forging(Process):
    """Class representing forging cycle"""

    TEMPLATE: ClassVar[ProcessTemplate] = ProcessTemplate(
        name="Forging",
        description="""Forging
                """,
    )

    _ATTRS: ClassVar[AttrsDict] = {"conditions": {}, "parameters": {}}

    finalize_template(_ATTRS, TEMPLATE)
