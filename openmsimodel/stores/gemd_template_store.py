# imports
import os
import csv
from pathlib import Path
from typing import Union
from dataclasses import dataclass

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


__all__ = ["GEMDTemplate", "GEMDTemplateStore"]


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


class GEMDTemplateStore:
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

    _root_folder = (
        Path(__file__).parent / "stores/templates"
    )  # TODO: put somehwere else

    store_folders = {
        PropertyTemplate: _root_folder / "property_templates",
        ConditionTemplate: _root_folder / "condition_templates",
        ParameterTemplate: _root_folder / "parameter_templates",
        MaterialTemplate: _root_folder / "material_templates",
        MeasurementTemplate: _root_folder / "measurement_templates",
        ProcessTemplate: _root_folder / "process_templates",
    }

    registry_path = _root_folder / "registry.csv"

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
            for template in os.listdir(template_type_root):
                # TODO: maybe read the path and pass it
                self.register_new_template_from_file(template)

    def register_new_template_from_file(self, template):
        """
        Add a new template that's been read from a file
        """
        if not isinstance_template(template):
            return
        name = template.name

        # if it has persistent_id, which means maybe being reused, just Add
        # if name similar, bring it up
        # if !name, and !unique id, and !not exactly the same as others, add and register

        # if (
        #     self.encoder.scope not in template.uids.keys()
        # ):  # TODO: maybe remove since there is a equivalent check in base node init()
        #     errmsg = f'ERROR: {type(template).__name__} {name} is missing a UID for scope "{self.encoder.scope}"!'
        #     raise RuntimeError(errmsg)

        dict_to_add_to = None
        if isinstance_attribute_template(template):
            dict_to_add_to = self.__attribute_templates[
                self.TempStringToTemp[template.typ]
            ]
        elif isinstance_object_template(template):
            dict_to_add_to = self.__object_templates[
                self.TempStringToTemp[template.typ]
            ]

        if dict_to_add_to is None:
            raise RuntimeError(f"ERROR: unrecognized template type {type(template)}!")

        # finding template by persistent_id match
        if "persistent_id" in template.uids.keys():
            assert "persistent_id" in dict_to_add_to[name].uids.keys()
            print(
                f"template with name {name}  sucessfully found in store by matching persistent_id: {template.uids['persistent_id']}."
            )
            pass

        # finding template by full match
        ordered_template = ordered(
            template
        )  # TODO: maybe remove persistent_Id key here from ordered_template/ or not necessary based on previous code block?
        for obj in dict_to_add_to.values():
            if ordered(obj) == ordered_template:
                print(
                    f"template with name {name} sucessfully found in store by matching its JSON content to a template in store. "
                )
            pass

        if (
            name in dict_to_add_to.keys()
        ):  # TODO: return a message if name is similar to one in bank
            raise RuntimeError(
                f"ERROR: template with name {name} already exists in store!"
            )

        # writing to registry
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

        # self.encoder.thin_dumps(self.store_folders[type(template)] / , indent=3)

        dict_to_add_to[name] = GEMDTemplate(template, True)
        self.__n_from_files += (
            1  # TODO: keep this incr but add just __n, and increment differently
        )

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


global_template_store = GEMDTemplateStore()
