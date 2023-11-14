from typing import Callable, Union, Type, Tuple
from gemd.entity.link_by_uid import LinkByUID
from gemd.entity.dict_serializable import DictSerializable

from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun

# from openmsimodel.entity.gemd.gemd_element import GEMDElement
from openmsimodel.utilities.typing import (
    Spec,
    Run,
    Template,
    AttrTemplate,
    ObjTemplate,
    AllGEMD,
    AllGEMDMinusAttr,
)


######### THE FUNCTION BELOW IS COPIED/PASTED FROM GEMD CODE #########
def cached_isinstance_generator(
    class_or_tuple: Union[Type, Tuple[Type]]
) -> Callable[[object], bool]:
    """
    Generate a function that checks and caches an isinstance(obj, class_or_tuple) call.

    Parameters
    ----------
    class_or_tuple: Union[Type, Tuple[Type]]
        A single type or a tuple of types

    Returns
    -------
    Callable[[object], bool]
        function with signature function(obj), returning isinstance(obj, class_or_tuple)

    """
    cache = dict()

    def func(obj):
        obj_type = type(obj)
        if obj_type not in cache:
            cache[obj_type] = isinstance(obj, class_or_tuple)
        return cache[obj_type]

    return func


# from openmsimodel.entity.gemd.process import Process
# from openmsimodel.entity.gemd.material import Material
# from openmsimodel.utilities.attributes import _validate_temp_keys, define_attribute

# Some cached isinstance functions to reduce overhead
# isinstance_base_element = cached_isinstance_generator([Element])

isinstance_all_gemd = cached_isinstance_generator(AllGEMD.__args__)
isinstance_all_gemd_minus_attr = cached_isinstance_generator(AllGEMDMinusAttr.__args__)

isinstance_template = cached_isinstance_generator(Template.__args__)
isinstance_attribute_template = cached_isinstance_generator(AttrTemplate.__args__)
isinstance_object_template = cached_isinstance_generator(ObjTemplate.__args__)
isinstance_spec = cached_isinstance_generator(Spec.__args__)
isinstance_run = cached_isinstance_generator(Run.__args__)

isinstance_link_by_uid = cached_isinstance_generator(LinkByUID)
isinstance_dict_serializable = cached_isinstance_generator(DictSerializable)

isinstance_material_run = cached_isinstance_generator(MaterialRun)
isinstance_ingredient_run = cached_isinstance_generator(IngredientRun)

isinstance_list_or_tuple = cached_isinstance_generator((list, tuple))
