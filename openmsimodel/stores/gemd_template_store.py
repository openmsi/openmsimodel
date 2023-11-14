# imports
import os, csv, json, warnings
import shutil
from pathlib import Path
from typing import Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

from gemd.util.impl import set_uuids
from gemd.json import GEMDJson
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate
from gemd.entity.template import MaterialTemplate, MeasurementTemplate, ProcessTemplate
from openmsimodel.utilities.typing import Template
from openmsimodel.utilities.cached_isinstance_functions import (
    isinstance_template,
    isinstance_attribute_template,
    isinstance_object_template,
)
from openmsimodel.entity.gemd.impl import assign_uuid
from openmsimodel.utilities.logging import Logger


# from openmsimodel.stores.common import GEMDTemplateStore, stores_config
class StoresConfig:
    """
    Managing the default configurations for activating store, name of the default store and a list of ids of all template stores

    Example:
    >>> from openmsimodel.stores.gemd_template_store import StoresConfig, stores_config
    >>> stores_config = StoresConfig(activated=True) # default name is local
    >>> stores_config.designated_store_id
    "local"
    >>> stores_config = StoresConfig(activated=True, designated_store_id="local_2")

    """

    all_template_stores: dict
    activated: bool
    designated_store_id: str
    designated_root: str

    def __init__(
        self,
        activated=False,
        designated_store_id: str = "local",
        designated_root: str = Path(__file__) / "stores/local",
    ):
        self.all_template_stores = {}
        self.activated = activated
        if self.activated:
            self.designated_store_id = designated_store_id
            self.designated_root = designated_root
            self.deploy_store(designated_store_id)

    def deploy_store(self, name):
        if name in self.all_template_stores.keys():
            raise NameError(f"template store with id {name} already exists.")
        self.all_template_stores[name] = GEMDTemplateStore(name, load_all_files=False)
        self.all_template_stores[name].root = self.designated_root
        self.all_template_stores[name].initialize_store()

    def register_store(self, store):
        if store.id in self.all_template_stores.keys():
            raise NameError(f"template store with id {store.name} already exists.")
        if self.activated:
            self.all_template_stores[store.id] = store
            self.all_template_stores[store.id].initialize_store()


stores_config = StoresConfig()

# TODO: chck types of errors returned


# TODO: maybe add file path, + from subclass?
@dataclass
class GEMDTemplate:  # TODO: move to typing
    template: Union[
        PropertyTemplate,
        ParameterTemplate,
        ConditionTemplate,
        MaterialTemplate,
        MeasurementTemplate,
        ProcessTemplate,
    ]
    from_file: bool
    from_store: bool
    from_memory: bool
    from_subclass: bool


# TODO: test if not root assigned


class GEMDTemplateStore(ABC):
    """
    A class to hold and work with a set of GEMD template objects. Allows easier loading from
    a template_type_root of json dump files coupled with one or more dictionaries of static, hard-coded templates
    """

    # _root = Path(__file__).parent / "stores/global"

    def __init__(self, id, encoder=GEMDJson(), load_all_files=False):
        """
        encoder = a pre-created GEMD JSON encoder (optional)
        """

        self.id = id
        self.encoder = encoder  # TODO: separate from science_kit one
        # self.logger = Logger()
        self._n_from_files = 0
        self._n_hardcoded = 0
        self._property_templates = {}
        self._parameter_templates = {}
        self._condition_templates = {}
        self._attribute_templates = {  # TODO: changes names to match with spec store
            PropertyTemplate: self._property_templates,
            ParameterTemplate: self._parameter_templates,
            ConditionTemplate: self._condition_templates,
        }
        self._material_templates = {}
        self._measurement_templates = {}
        self._process_templates = {}
        self._object_templates = {
            MaterialTemplate: self._material_templates,
            MeasurementTemplate: self._measurement_templates,
            ProcessTemplate: self._process_templates,
        }
        if load_all_files:
            self.register_all_templates_from_store()
        if stores_config.activated:
            stores_config.register_store(self)

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, path: str):
        # TODO raise error if not exists?
        self._root = path

    @property
    def registry_path(self):
        return self._root / "registry.csv"

    @property
    def registry_columns(self):
        return ["persistent_id", "name", "type"]

    @property
    def store_folders(self):
        return {
            PropertyTemplate: self._root / "property_templates",
            ConditionTemplate: self._root / "condition_templates",
            ParameterTemplate: self._root / "parameter_templates",
            MaterialTemplate: self._root / "material_templates",
            MeasurementTemplate: self._root / "measurement_templates",
            ProcessTemplate: self._root / "process_templates",
        }

    TempStringToTemp = {  # TODO: move to typing
        "property_template": PropertyTemplate,
        "condition_template": ConditionTemplate,
        "parameter_template": ParameterTemplate,
        "measurement_template": MeasurementTemplate,
        "material_template": MaterialTemplate,
        "process_template": ProcessTemplate,
    }

    def register_all_templates_from_store(self):
        """
        loads all templates supposed to reside as files from store folder
        """
        # TODO: use the registered hardtemplates
        for template_type in self._object_templates.keys():
            template_type_root = self.store_folders[template_type]
            for template_name in os.listdir(template_type_root):
                # TODO: maybe read the path and pass it
                with open(
                    os.path.join(template_type_root, template_name), "r"
                ) as template_file:  # TODO: change to regular load
                    template = json.dumps((json.load(template_file)))
                    template = self.encoder.raw_loads(template)
                self.register_new_template(template, from_file=True, from_store=True)

    def register_new_template(
        self,
        template: Template,
        from_file=False,
        from_store=False,
        from_memory=False,
        from_subclass=False,
    ):
        """
        Add a new template that's been read from a file
        """
        if not isinstance_template(template):
            errmsg = f' : Excepted an AttributeTemplate or BaseTemplate but got "{type(template).__name__}"!'
            raise TypeError(errmsg)
        name = template.name

        if self.encoder.scope not in template.uids.keys():
            assign_uuid(
                template, "auto"
            )  # TODO: fix this, has nothing to do with encoder. just change to if "auto"?

        dict_to_add_to = None
        if isinstance_attribute_template(
            template
        ):  # TODO: use instance or use the existence of a type key, which would make it conform but loss actual type specificity
            dict_to_add_to = self._attribute_templates[
                self.TempStringToTemp[template.typ]
            ]
        elif isinstance_object_template(template):
            dict_to_add_to = self._object_templates[self.TempStringToTemp[template.typ]]

        if dict_to_add_to is None:
            raise RuntimeError(f"ERROR: unrecognized template type {type(template)}!")

        if (
            name in dict_to_add_to.keys()
        ):  # TODO: return a message if name is similar to one in bank
            warning_msg = f"WARNING: template with name '{name}' already exists in store and will be used. "
            warnings.warn(
                warning_msg,
                ResourceWarning,
            )
            if (
                self.encoder.scope not in dict_to_add_to[name].template.uids
            ):  # FIXME: is this to handle in case any kind of files comes in?
                warning_msg = f"WARNING: template with name '{name}' found in store doesn't have {self.encoder.scope} uid."
                warnings.warn(
                    warning_msg,
                    ResourceWarning,
                )
            dict_to_add_to[name].from_memory = False
            dict_to_add_to[name].from_subclass = False
            dict_to_add_to[name].from_store = True
            return dict_to_add_to[name]

        if from_store:  # TODO: change to from_store
            # dict_to_add_to[name] = GEMDTemplate(template, True)
            self._n_from_files += 1  # TODO: keep this incr but add to __n for all, and increment differently
        else:
            # TODO: this is always going to be false if not in dict. just compare without name
            # finding template by full match
            # has_matching_template = False
            # ordered_template = ordered(
            #     template
            # )  # TODO: maybe remove persistent_id key here from ordered_template/ or not necessary based on previous code block?
            # # TODO: use hash comparison instead?
            # for obj in dict_to_add_to.values():
            #     if ordered(obj) == ordered_template:
            #         has_matching_template = True
            #         matching_template = obj
            #         self.logger.info(
            #             f"template '{name}' sucessfully found in store by matching its JSON content to a template in store. "
            #         )
            #         return matching_template

            # writing to registry
            # TODO: convert to dataframe manipulation to be safer
            with open(self.registry_path, "r+") as registry_csv_file:
                persistent_id = len(registry_csv_file.readlines()) - 1
                template.add_uid(
                    "persistent_id", persistent_id
                )  # TODO: maybe make sure it's not there?
                registry_writer = csv.writer(registry_csv_file, delimiter=",")
                registry_writer.writerow([persistent_id, name, template.typ])

            # writing template to file
            with open(
                self.store_folders[type(template)] / f"{name}_pid_{persistent_id}.json",
                "w",  # TODO: maybe use diff encoding of path
            ) as template_file:
                template_file.write(self.encoder.thin_dumps(template, indent=3))

        dict_to_add_to[name] = GEMDTemplate(
            template, from_file, from_store, from_memory, from_subclass
        )

        return dict_to_add_to[
            name
        ]  # TODO: maybe return full template and keep info about the template, like from_store, path, etc

    # @classmethod
    # @abstractmethod ?
    # shutil can cause problems down the road? permissions, etc
    def initialize_store(self):
        # TODO raise error if not exists
        if os.path.isdir(self.root):
            shutil.rmtree(self.root)
        os.mkdir(self.root)
        for subfolder in self.store_folders.values():
            os.mkdir(subfolder)
        with open(self.registry_path, "w") as registry_csv_file:
            registry_writer = csv.writer(registry_csv_file, delimiter=",")
            registry_writer.writerow(self.registry_columns)

    def add_missing_hardcoded_templates(self, attr_hardcoded, obj_hardcoded):
        """
        Add any templates in the hardcoded dictionary that haven't already been added from a deserialization step

        attr_hardcoded = a dictionary of hard-coded attribute templates, some of which may have been
            used previously and dumped as json into dirpath
        obj_hardcoded = a dictionary of hard-coded object templates, some of which may have been used
            previously and dumped as json into dirpath
        """
        self.__add_missing_templates(attr_hardcoded)
        self.__add_missing_templates(obj_hardcoded)

    def attr(self, template_name):
        """
        Return an attribute template given its name
        """
        try:
            return self._attribute_templates[template_name].template
        except KeyError:
            raise ValueError(
                f'ERROR: no stored attribute template called "{template_name}"'
            )

    def obj(self, template_name):
        """
        Return an object template given its name
        """
        try:
            for template_type in self._object_templates.keys():
                return self._object_templates[template_type][template_name].template
        except KeyError:
            raise ValueError(
                f'ERROR: no stored object template called "{template_name}"'
            )

    def __add_missing_templates(self, hardcoded):
        names_seen = set()
        for name, template in hardcoded.items():
            if name in names_seen:
                raise ValueError(
                    f"ERROR: harcoded template dictionary duplicates template name {name}!"
                )
            else:
                names_seen.add(name)
            if template.uids is not None and self.encoder.scope in template.uids.keys():
                errmsg = f'ERROR: "{self.encoder.scope}" scope UID has already been set for a hard-coded template!'
                raise RuntimeError(errmsg)
            dict_to_add_to = None
            if isinstance_attribute_template(template):
                dict_to_add_to = self._attribute_templates[
                    self.TempStringToTemp[template["type"]]
                ]
            elif isinstance_object_template(template):
                dict_to_add_to = self._object_templates[
                    self.TempStringToTemp[template["type"]]
                ]
            if dict_to_add_to is None:
                raise RuntimeError(
                    f"ERROR: unrecognized template type {type(template)}!"
                )
            if name in dict_to_add_to.keys():
                continue
            set_uuids(template, self.encoder.scope)
            dict_to_add_to[name] = GEMDTemplate(template, False)
            self._n_hardcoded += 1

    @property
    def n_from_files(self):
        return self._n_from_files

    @property
    def n_hardcoded(self):
        return self._n_hardcoded

    @property
    def all_templates(self):
        both_dicts = [self._attribute_templates, self._object_templates]
        for tempdict in both_dicts:
            for template_type in tempdict.keys():
                for name in tempdict[template_type].keys():
                    yield tempdict[template_type][name].template

    @property
    def all_read_templates(self):
        both_dicts = [self._attribute_templates, self._object_templates]
        for tempdict in both_dicts:
            for template_type in tempdict.keys():
                for name in tempdict[template_type].keys():
                    if tempdict[template_type][name].from_store:
                        yield tempdict[template_type][name].template
