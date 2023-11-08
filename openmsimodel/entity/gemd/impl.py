import uuid
from gemd.util.impl import recursive_foreach


def assign_uuid(obj, scope):
    """
    Recursively assign a uuid to every BaseEntity that doesn't already contain a uuid.

    This ensures that all of the pointers in the object can be replaced with LinkByUID objects

    Parameters
    ----------
    obj: BaseEntity
        object to recursively assign uuids to
    scope: str
        scope of the uuid to assign

    Returns
    -------
    None

    """

    def func(base_obj):
        if not (scope in base_obj.uids.keys()):
            #     base_obj.uids[scope] = {}
            # if len(base_obj.uids[scope]) == 0:
            base_obj.add_uid(scope, str(uuid.uuid4()))
        return

    recursive_foreach(obj, func)
    return
