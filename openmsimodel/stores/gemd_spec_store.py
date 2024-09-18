import copy, methodtools
from typing import Union
from dataclasses import dataclass
from gemd.util.impl import set_uuids, recursive_foreach
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.json import GEMDJson
from openmsimodel.stores.cached_isinstance_functions import isinstance_spec
from abc import ABC, abstractmethod
from pathlib import Path
import os, shutil, csv

@dataclass
class GEMDSpec :
    spec : Union[MaterialSpec,ProcessSpec,IngredientSpec,MeasurementSpec]
    as_dict_no_uid : str
    from_file: bool

class GEMDSpecStore(ABC) :
    """
    A class to hold and work with a set of GEMD spec objects. Allows easier loading from 
    a directory of json dump files coupled with dynamically-created specs
    """

    _root = Path(__file__).parent / "local"

    def __init__(self, id, root=None, encoder=GEMDJson(),debug=False, stores_config=None, load_all_files=False) :
        self.id = id
        if root:
            self.root = root
        self.encoder = encoder
        self.__n_specs = 0
        self.__mat_specs = {}
        self.__proc_specs = {}
        self.__ing_specs = {}
        self.__meas_specs = {}
        self._object_templates = {
            MaterialSpec : self.__mat_specs,
            ProcessSpec : self.__proc_specs,
            IngredientSpec : self.__ing_specs,
            MeasurementSpec : self.__meas_specs,
        }
        self.__debug=debug
        if load_all_files:
            self.register_all_specs_from_store()
        if stores_config and stores_config.activated:
            self.stores_config = stores_config
            self.stores_config.register_store(self)

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, path: str):
        # TODO raise error if not exists?
        self._root = Path(path)

    @property
    def registry_path(self):
        return self._root / "spec_registry.csv"
    
    @property
    def registry_columns(self):
        return ["persistent_id", "name", "type"]
    
    @property
    def store_folders(self):
        return {
            MaterialSpec: self._root / "material_specs",
            ProcessSpec: self._root / "process_specs",
            IngredientSpec: self._root / "ingredient_specs",
            MeasurementSpec: self._root / "measurement_specs",
        }

    TempStringToTemp = {  # TODO: move to typing
        "material_spec": MaterialSpec,
        "process_spec": ProcessSpec,
        "ingredient_spec": IngredientSpec,
        "measurement_spec": MeasurementSpec,
    }

    def initialize_store(self):
        # TODO raiseinitialize_store error if not exists
        # if os.path.isdir(self.root):
        #     shutil.rmtree(self.root)
        # os.mkdir(self.root)
        for subfolder in self.store_folders.values():
            os.mkdir(subfolder)
        with open(self.registry_path, "w") as registry_csv_file:
            registry_writer = csv.writer(registry_csv_file, delimiter=",")
            registry_writer.writerow(self.registry_columns)

    @property
    def n_specs(self) :
        return self.__n_specs
    @property
    def all_specs(self) :
        for specdict in self._object_templates.values() :
            for name in specdict.keys() :
                for uid in specdict[name].keys() :
                    yield specdict[name][uid].spec
    @property
    def all_read_specs(self) :
        for specdict in self._object_templates.values() :
            for name in specdict.keys() :
                for uid in specdict[name].keys() :
                    if specdict[name][uid].from_file :
                        yield specdict[name][uid].spec

    def unique_version_of(self,specobj,debug=False,recursive_check=True,recursive_register=True) :
        """
        Returns a unique version of specobj by searching through the currently defined specs.
        If an already-existing object is identical to specobj, returns that object. 
        If specobj is unique w.r.t. what's already existing then that object is registered in the store and returned.

        specobj = the Spec object that should be registered or replaced with its corresponding unique object
        debug = True to print debugging statements
        recursive_check = True is any Spec objects linked to this object should also be checked for uniqueness
        recursive_register = True if any Spec objects linked to this object should be registered in the store
        """
        self.__debug = debug
        #check if an identical spec has been registered, and return it if so
        if recursive_check :
            if self.__spec_exists_in_store_rec(specobj) :
                return (self.__get_stored_version_of_spec(specobj,debug=debug)).spec
        else :
            existingspec = self.__get_stored_version_of_spec(specobj,debug=debug)
            if existingspec is not None :
                return existingspec.spec
        #if an existing spec wasn't returned, register this spec as a new one and then return it
        if recursive_register :
            recursive_foreach(specobj,self.__register_new_unique_specs,apply_first=True)
        else :
            self.__register_new_unique_specs(specobj)
        existingspec = self.__get_stored_version_of_spec(specobj,debug=debug)
        return existingspec

    def register_new_unique_spec_from_file(self,item) :
        if not isinstance_spec(item) :
            return
        if self.__get_stored_version_of_spec(item) is not None :
            return
        self.__register_spec(item,from_file=True)

    def remove_unneeded_spec(self,item) :
        if not isinstance_spec(item) :
            return
        if self.encoder.scope not in item.uids.keys() :
            errmsg = f'ERROR: {type(item).__name__} {item.name} is missing a UID for scope "{self.encoder.scope}"'
            raise RuntimeError(errmsg)
        name = item.name
        uid = item.uids[self.encoder.scope]
        dict_to_use = self._object_templates[type(item)]
        if name not in dict_to_use.keys() :
            raise RuntimeError(f'ERROR: no {type(item).__name__} with name {name} found in spec store!')
        elif uid not in dict_to_use[name].keys() :
            raise RuntimeError(f'ERROR: no {type(item).__name__} {name} with UID {uid} found in spec store!')
        _ = dict_to_use[name].pop(uid)
        self.__n_specs-=1

    def __get_spec_dict_no_uids(self,specobj) :
        """
        Return a version of a Spec object serialized to a string representation of a 
        dictionary where all UIDs of the relevant encoder scope have been removed
        """
        spec_copy = copy.deepcopy(specobj)
        recursive_foreach(spec_copy,self.__scrub_uids)
        return str(spec_copy)

    def __scrub_uids(self,item) :
        if not isinstance_spec(item) :
            return
        if self.encoder.scope in item.uids.keys() :
            _ = item.uids.pop(self.encoder.scope)

    @methodtools.lru_cache(maxsize=256)
    def __get_name_and_dict_for_spec(self,specobj) :
        return specobj.name, self.__get_spec_dict_no_uids(specobj)

    def __get_stored_version_of_spec(self,specobj,debug=False) :
        new_spec_name, new_spec_as_dict_no_uid = self.__get_name_and_dict_for_spec(specobj)
        dict_of_type = self._object_templates[type(specobj)]
        if new_spec_name in dict_of_type.keys() :
            dict_to_search = dict_of_type[new_spec_name]
            if self.encoder.scope in specobj.uids.keys() :
                if specobj.uids[self.encoder.scope] in dict_to_search.keys() :
                    if debug :
                        msg = f'Returning an existing {type(specobj).__name__} with name {new_spec_name} '
                        msg+= f'({specobj.uids[self.encoder.scope]}) (found by UID)'
                        print(msg)
                    return dict_to_search[specobj.uids[self.encoder.scope]]
                return None
            for existingspec in dict_to_search.values() :
                if (existingspec.spec==specobj) :
                    if debug :
                        msg = f'Returning an existing {type(specobj).__name__} with name {new_spec_name} '
                        msg+= f'({existingspec.spec.uids[self.encoder.scope]}) (found by spec comp)'
                        print(msg)
                    return existingspec
                elif (existingspec.as_dict_no_uid==new_spec_as_dict_no_uid) :
                    if debug :
                        msg = f'Returning an existing {type(specobj).__name__} with name {new_spec_name} '
                        msg+= f'({existingspec.spec.uids[self.encoder.scope]}) '
                        msg+= '(found by dict comp)'#:{existingspec.as_dict_no_uid} and \n{new_spec_as_dict_no_uid})'
                        print(msg)
                    return existingspec
        return None

    def __spec_exists_in_store_rec(self,specobj) :
        self.__n_objs_searched = 0
        self.__n_objs_found = 0
        recursive_foreach(specobj,self.__check_spec_exists_in_store,apply_first=True)
        if self.__n_objs_searched==self.__n_objs_found :
            return True
        return False

    def __check_spec_exists_in_store(self,item) :
        if self.__n_objs_found<self.__n_objs_searched :
            return
        elif not isinstance_spec(item) :
            return
        self.__n_objs_searched+=1
        stored_version = self.__get_stored_version_of_spec(item)
        if stored_version is not None :
            self.__n_objs_found+=1

    def register_new_unique_specs(self,item) :
        if not isinstance_spec(item) :
            raise TypeError
        if self.__spec_exists_in_store_rec(item) :
            return self.__get_stored_version_of_spec(item)
        spec_dataclass = self.__register_spec(item)
        spec = spec_dataclass.spec
        name = spec.name
        # writing to registry
        with open(self.registry_path, "r+") as registry_csv_file:
            persistent_id = len(registry_csv_file.readlines()) - 1
            spec.add_uid(
                "persistent_id", persistent_id
            )  # TODO: maybe make sure it's not there?
            registry_writer = csv.writer(registry_csv_file, delimiter=",")
            registry_writer.writerow([persistent_id, name, spec.typ])

        # writing spec to file
        with open(
            self.store_folders[type(spec)] / f"{name}_pid_{persistent_id}.json",
            "w",  # TODO: maybe use diff encoding of path
        ) as spec_file:
            spec_file.write(self.encoder.thin_dumps(spec, indent=3))
        spec_dataclass.spec = spec
        return spec_dataclass
        

    def __register_spec(self,item,from_file=False) :
        new_spec_name, new_spec_as_dict_no_uid = self.__get_name_and_dict_for_spec(item)
        dict_of_type = self._object_templates[type(item)]
        if new_spec_name not in dict_of_type.keys() :
            dict_of_type[new_spec_name] = {}
        set_uuids(item,self.encoder.scope)
        new_uid = item.uids[self.encoder.scope]
        if self.__debug :
            print(f'Creating a new {type(item).__name__} with name {new_spec_name} ({new_uid})')
        dict_of_type[new_spec_name][new_uid] = GEMDSpec(item,new_spec_as_dict_no_uid,from_file)
        self.__n_specs+=1
        return dict_of_type[new_spec_name][new_uid]
    