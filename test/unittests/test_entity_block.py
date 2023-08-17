# imports
import pkg_resources, subprocess, unittest, sys, importlib

sys.path.insert(0, "..")
from data.subclassing.incomplete_subclass import incompleteSubclass
from data.subclassing.erroneous_subclass_1 import erroneousSubclass1
from data.subclassing.arcmelting_example_subclass import ArcMeltingExample

from openmsimodel.entity.base import (
    BaseNode,
    Process,
    Measurement,
    Ingredient,
    Material,
)

from gemd import (
    NominalCategorical,
    NominalReal,
    CategoricalBounds,
    ProcessRun,
    ProcessSpec,
    ProcessTemplate,
    MaterialTemplate,
    MeasurementTemplate,
    Parameter,
    ParameterTemplate,
    Property,
    PropertyTemplate,
    Condition,
    ConditionTemplate,
)
from gemd.json import GEMDJson
from gemd.entity.util import make_instance
