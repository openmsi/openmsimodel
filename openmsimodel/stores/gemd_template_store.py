# imports
import os, csv, json
import shutil
from pathlib import Path
from typing import Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

from gemd.util.impl import set_uuids
from gemd.json import GEMDJson
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate
from gemd.entity.template import MaterialTemplate, MeasurementTemplate, ProcessTemplate
from .cached_isinstance_functions import (
    isinstance_template,
    isinstance_attribute_template,
    isinstance_object_template,
)
from openmsimodel.entity.base.impl import assign_uuid
from ..utilities.logging import Logger

__all__ = ["GEMDTemplate", "GEMDTemplateStore"]


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


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


class GEMDTemplateStore(ABC):
    """
    A class to hold and work with a set of GEMD template objects. Allows easier loading from
    a template_type_root of json dump files coupled with one or more dictionaries of static, hard-coded templates
    """

    @property
    def n_from_files(self):
        return self.__n_from_files

    @property
    def n_hardcoded(self):
        return self.__n_hardcoded

    @property
    def all_templates(self):
        both_dicts = [self.__attribute_templates, self.__object_templates]
        for tempdict in both_dicts:
            for template_type in tempdict.keys():
                for name in tempdict[template_type].keys():
                    yield tempdict[template_type][name].template

    @property
    def all_read_templates(self):
        both_dicts = [self.__attribute_templates, self.__object_templates]
        for tempdict in both_dicts:
            for template_type in tempdict.keys():
                for name in tempdict[template_type].keys():
                    if tempdict[template_type][name].from_file:
                        yield tempdict[template_type][name].template

    _root_folder = property(Path(__file__).parent / "stores/templates")

    @property
    def root_folder(self):
        return self._root_folder

    def set_root(self, path):
        # TODO raise error if not exists
        self._root_folder = path

    @property
    def registry_path(self):
        return self._root_folder / "registry.csv"

    @property
    def registry_columns(self):
        return ["persistent_id", "name"]

    @property
    def store_folders(self):
        return {
            PropertyTemplate: self._root_folder / "property_templates",
            ConditionTemplate: self._root_folder / "condition_templates",
            ParameterTemplate: self._root_folder / "parameter_templates",
            MaterialTemplate: self._root_folder / "material_templates",
            MeasurementTemplate: self._root_folder / "measurement_templates",
            ProcessTemplate: self._root_folder / "process_templates",
        }
        # return self._store_folders

    # @classmethod
    # @abstractmethod ?
    # shutil can cause problems down the road? permissions, etc
    def initialize_store(self, root):
        # TODO raise error if not exists
        if os.path.isdir(root):
            shutil.rmtree(root)
        os.mkdir(root)
        for subfolder in self.store_folders.values():
            os.mkdir(subfolder)

            # persistent_id = len(registry_csv_file.readlines()) - 1
            #     template.add_uid("persistent_id", persistent_id)
            #     registry_writer = csv.writer(registry_csv_file, delimiter=",")
            #     registry_writer.writerow([persistent_id, name])

        with open(cls.registry_path, "w") as registry_csv_file:
            registry_writer = csv.writer(registry_csv_file, delimiter=",")
            registry_writer.writerow(cls.registry_columns)

    # _store_folders = {
    #     PropertyTemplate: self._root_folder / "property_templates",
    #     ConditionTemplate: self._root_folder / "condition_templates",
    #     ParameterTemplate: self._root_folder / "parameter_templates",
    #     MaterialTemplate: self._root_folder / "material_templates",
    #     MeasurementTemplate: self._root_folder / "measurement_templates",
    #     ProcessTemplate: self._root_folder / "process_templates",
    # }

    # _registry_path = self._root_folder / "registry.csv"

    TempStringToTemp = {  # TODO: move to typing
        "property_template": PropertyTemplate,
        "condition_template": ConditionTemplate,
        "parameter_template": MaterialTemplate,
        "measurement_template": MeasurementTemplate,
        "material_template": MaterialTemplate,
        "process_template": ProcessTemplate,
    }

    def __init__(self, encoder=GEMDJson(), load_all_files=True):
        """
        encoder = a pre-created GEMD JSON encoder (optional)
        """
        self.encoder = encoder  # TODO: separate from workflow one
        self.logger = Logger()
        self.__n_from_files = 0
        self.__n_hardcoded = 0
        self._property_templates = {}
        self._parameter_templates = {}
        self._condition_templates = {}
        self.__attribute_templates = {  # TODO: changes names to match with spec store
            PropertyTemplate: self._property_templates,
            ParameterTemplate: self._parameter_templates,
            ConditionTemplate: self._condition_templates,
        }
        self._material_templates = {}
        self._measurement_templates = {}
        self._process_templates = {}
        self.__object_templates = {
            MaterialTemplate: self._material_templates,
            MeasurementTemplate: self._measurement_templates,
            ProcessTemplate: self._process_templates,
        }
        if load_all_files:
            self.register_all_templates_from_files()

    def register_all_templates_from_files(self):
        """
        loads all templates supposed to reside as files from preset folders
        """
        # TODO: use the registered hardtemplates
        for template_type in self.__object_templates.keys():
            template_type_root = self.store_folders[template_type]
            for template_name in os.listdir(template_type_root):
                # TODO: maybe read the path and pass it
                with open(
                    os.path.join(template_type_root, template_name), "r"
                ) as template_file:  # TODO: change to regular load
                    template = json.dumps((json.load(template_file)))
                    template = self.encoder.raw_loads(template)
                self.register_new_template(template, from_file=True)

    # def validate_template(self, template):

    def register_new_template(self, template, from_file=False):
        """
        Add a new template that's been read from a file
        """
        if not isinstance_template(template):
            return
        name = template.name

        if (
            self.encoder.scope not in template.uids.keys()
        ):  # TODO: maybe remove since there is a equivalent check in base node init()
            errmsg = f'ERROR: {type(template).__name__} {name} is missing a UID for scope "{self.encoder.scope}"!'
            raise RuntimeError(errmsg)

        dict_to_add_to = None
        if isinstance_attribute_template(
            template
        ):  # TODO: use instance or use the existence of a type key, which would make it conform but loss actual type specificity
            dict_to_add_to = self.__attribute_templates[
                self.TempStringToTemp[template.typ]
            ]
        elif isinstance_object_template(template):
            dict_to_add_to = self.__object_templates[
                self.TempStringToTemp[template.typ]
            ]

        if dict_to_add_to is None:
            raise RuntimeError(f"ERROR: unrecognized template type {type(template)}!")

        if (
            name in dict_to_add_to.keys()
        ):  # TODO: return a message if name is similar to one in bank
            raise NameError(
                f"ERROR: template with name {name} already exists in store! "
            )

        if from_file:
            dict_to_add_to[name] = GEMDTemplate(template, True)
            self.__n_from_files += (
                1  # TODO: keep this incr but add just __n, and increment differently
            )
        else:
            # TODO: this is always going to be false if not is not in dict. just compare without name
            # finding template by full match
            has_matching_template = False
            ordered_template = ordered(
                template
            )  # TODO: maybe remove persistent_id key here from ordered_template/ or not necessary based on previous code block?
            for obj in dict_to_add_to.values():
                if ordered(obj) == ordered_template:
                    has_matching_template = True
                    matching_template = obj
                    self.logger.info(
                        f"template with name {name} sucessfully found in store by matching its JSON content to a template in store. "
                    )
                    return matching_template.template

            # writing to registry
            # TODO: convert to dataframe manipulation to be safer
            with open(self.registry_path, "r+") as registry_csv_file:
                persistent_id = len(registry_csv_file.readlines()) - 1
                template.add_uid("persistent_id", persistent_id)
                registry_writer = csv.writer(registry_csv_file, delimiter=",")
                registry_writer.writerow([persistent_id, name])

            # writing template to file
            with open(
                self.store_folders[type(template)] / f"{name}_{persistent_id}.json",
                "w",  # TODO: maybe use diff encoding of path
            ) as template_file:
                template_file.write(self.encoder.thin_dumps(template, indent=3))

            dict_to_add_to[name] = GEMDTemplate(template, False)
        return dict_to_add_to[name].template

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
            return self.__attribute_templates[template_name].template
        except KeyError:
            raise ValueError(
                f'ERROR: no stored attribute template called "{template_name}"'
            )

    def obj(self, template_name):
        """
        Return an object template given its name
        """
        try:
            for template_type in self.__object_templates.keys():
                return self.__object_templates[template_type][template_name].template
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
                dict_to_add_to = self.__attribute_templates[
                    self.TempStringToTemp[template["type"]]
                ]
            elif isinstance_object_template(template):
                dict_to_add_to = self.__object_templates[
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
            self.__n_hardcoded += 1


# global_template_store = GEMDTemplateStore()
