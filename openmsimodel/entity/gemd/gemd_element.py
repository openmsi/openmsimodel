"""
This module defines the `GEMDElement` class, which serves as a foundational element for materials, processes, and measurements in the GEMD (Graphical Expression of Materials Data) framework. 

The class provides functionality for creating, updating, linking, and outputting these entities. 

It includes methods for managing attributes such as properties, tags, and file links, making it a versatile tool for working with materials data.
"""

import os, warnings
from abc import abstractmethod
from typing import ClassVar, Type, Optional

from gemd import FileLink, Property
from gemd.entity.attribute.base_attribute import BaseAttribute
from gemd.entity.util import make_instance

from openmsimodel.entity.core_element import CoreElement

0
from openmsimodel.entity.gemd.impl import assign_uuid
from openmsimodel.utilities.cached_isinstance_functions import (
    isinstance_template,
    isinstance_spec,
    isinstance_run,
)
from openmsimodel.utilities.typing import (
    Template,
    Spec,
    Run,
    SpecOrRun,
    SpecOrRunLiteral,
)
from openmsimodel.utilities.attributes import (
    AttrsDict,
    validate_state,
    update_attrs,
    remove_attrs,
    _validate_temp_keys,
    define_attribute,
    finalize_template,
)

from openmsimodel.utilities.logging import Logger
import openmsimodel.stores.stores_config as stores_tools


class GEMDElement(CoreElement):
    """
    Base class for materials, processes, and measurements.

    ``GemdElement`` 's are thin wrappers for GEMD entities. One ``GemdElement`` contains
    a template, spec, and run for the same kind of entity (``Material``,
    ``Process``, or ``Measurement``) and helps to create, update, link, and
    output these.

    Note that `name` is the GEMD name given to the spec and run. The template
    name is the name of the subclass.

    To subclass in a file:

        1. Instantiate ``TEMPLATE`` as follows:
        ``TEMPLATE: ClassVar[Template] = Template(name=__name__)``,
        replacing ``Template`` with one of ``MaterialTemplate``,
        ``ProcessTemplate``, or ``MeasurementTemplate``.

        2. Instantiate ``_ATTRS`` as follows:
        ``_ATTRS``: ClassVar[AttrsDict] = _validate_temp_keys(TEMPLATE)

        3. Add conditions, parameters, and/or properties using
        ``define_attribute(_ATTRS, ...)`` from the ``qf_gemd.base.attributes``
        module.

        4. Call ``finalize_template(_ATTRS, TEMPLATE)``, found in the
        ``qf_gemd.base.attributes`` module, to add attributes to ``TEMPLATE``.

    Otherwise, instantiate in code by passing a template.

    """

    _TempType: ClassVar[Type[Template]]
    _SpecType: ClassVar[Type[Spec]]
    _RunType: ClassVar[Type[Run]]

    TEMPLATE: ClassVar[Template]

    _ATTRS: ClassVar[AttrsDict] = {}

    # TODO: remove and put somewhere
    _TAG_SEP: ClassVar[str] = "::"

    def __init__(
        self,
        name: str,
        *,
        template: ClassVar[
            Template
        ] = None,  # TODO: triple check with abc's hastemplate
        notes: Optional[str] = None,
        is_not_ingredient: bool = True,
    ) -> None:
        """Initializes a new instance of the GEMDElement class with the specified name, optional notes, and a flag indicating whether it is an ingredient.
        Optionally, a template can be provided to initialize the element with specific properties, parameters, and conditions.
        """
        super().__init__()

        self.name = name
        self.logger = Logger()
        self.TEMPLATE_WRAPPER = {}
        self.SPEC_WRAPPER = {}
        has_subclassed_template = hasattr(self, "TEMPLATE")

        if is_not_ingredient:  # FIXME without passed attribute
            if not has_subclassed_template and not template:
                # TODO: Change msg
                raise AttributeError(
                    f"TEMPLATE is not defined. Assign 'template' parameter, or create a new subclass with a defined TEMPLATE attribute."
                )

            if template:
                if has_subclassed_template:
                    warnings.warn(
                        f"Found template '{self.TEMPLATE.name}', but '{template.name}' will be used instead.",
                        ResourceWarning,
                    )
                self.TEMPLATE = template
                # FIXME: keep persistent id as reserved?

            # TODO: change from file when supporting file links
            # registering the object templates
            if stores_tools.stores_config.activated:
                for i, store in enumerate(
                    stores_tools.stores_config.all_template_stores.values()
                ):
                    self.TEMPLATE_WRAPPER[store.id] = store.register_new_template(
                        self.TEMPLATE,
                        from_file=False,
                        from_store=False,
                        from_memory=bool(template),
                        from_subclass=bool(has_subclassed_template and not template),
                    )
                    if stores_tools.stores_config.designated_store_id == store.id:
                        self.TEMPLATE = self.TEMPLATE_WRAPPER[
                            stores_tools.stores_config.designated_store_id
                        ].template

            if (
                template
            ):  # FIXME: maybe dont need to check, just call all the time? even if redundant?
                self.prepare_attrs()

            # registering the attribute templates
            if stores_tools.stores_config.activated:
                for i, store in enumerate(
                    stores_tools.stores_config.all_template_stores.values()
                ):
                    for _attr_type in self._ATTRS.keys():
                        for _attr in self._ATTRS[_attr_type].values():
                            stores_tools.stores_config.all_template_stores[
                                store.id
                            ].register_new_template(_attr["obj"])

            self._spec: Spec = self._SpecType(name=name, template=self.TEMPLATE)
            if stores_tools.stores_config.activated:
                for i, store in enumerate(
                    stores_tools.stores_config.all_spec_stores.values()
                ):
                    self.SPEC_WRAPPER[store.id] = store.register_new_unique_specs(self._spec)
                    if stores_tools.stores_config.designated_store_id == store.id:
                        self._spec = self.SPEC_WRAPPER[
                            stores_tools.stores_config.designated_store_id
                        ].spec
            self._run: Run = make_instance(self._spec)
            assign_uuid(self._spec, "auto")
            assign_uuid(self._run, "auto")  # FIXME: redundant?

    def generate_new_spec_run(self):
        if hasattr(self, "TEMPLATE"):
            self._spec: Spec = self._SpecType(name=self.name, template=self.TEMPLATE)
        else:
            self._spec: Spec = self._SpecType(name=self.name)
        self._run: Run = make_instance(self._spec)
        assign_uuid(self._spec, "auto")
        assign_uuid(self._run, "auto")  # FIXME: redundant?
        self.assert_linked()
        return self

    @property
    # @abstractmethod
    def template(self) -> Template:
        """Returns the underlying GEMD template associated with the element."""
        return self.TEMPLATE

    @property
    # @abstractmethod
    def spec(self) -> Spec:
        """Returns the underlying GEMD spec associated with the element."""
        return self._spec

    @property
    # @abstractmethod
    def run(self) -> Run:
        """Returns the underlying GEMD run associated with the element."""
        return self._run

    @property
    def assets(self) -> list:
        """Returns a list of assets associated with the element, including the template, spec, and run."""
        _assets = []
        if self.__class__.__name__ == "Ingredient":
            return [self.spec, self.run]
        else:
            _assets = [self.TEMPLATE, self.spec, self.run]
        return _assets

    def assert_linked(self, uuid_key="auto"):
        """
        Checks if the spec and run are properly linked to their templates using the specified UUID key.

        Parameters:
            uuid_key (str, optional): The UUID key to check for linking. Defaults to "auto".
        """
        if (
            uuid_key in self.spec.template.uids.keys()
            and uuid_key in self.TEMPLATE.uids.keys()
        ):
            if not self.spec.template.uids[uuid_key] == self.TEMPLATE.uids[uuid_key]:
                print(
                    f"spec's template is not linked to template by uuid key: {uuid_key}"
                )
            else:
                print("template and spec are linked properly.")
        else:
            print(f"uuid key: {uuid_key} not found in either templates.")

        if uuid_key in self.run.spec.uids.keys() and uuid_key in self.spec.uids.keys():
            if not self.run.spec.uids[uuid_key] == self.spec.uids[uuid_key]:
                print(f"run's spec is not linked to spec by uuid key: {uuid_key}")
            else:
                print("run and spec are linked properly.")
        else:
            print(f"uuid key: {uuid_key} not found in either specs.")

    ############################### ATTRIBUTES ###############################
    def update_attributes(
        self,
        AttrType: Type[BaseAttribute],
        attributes: tuple[BaseAttribute],
        replace_all: bool = False,
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """Updates the attributes of the spec or run with the specified attributes of the given attribute type (e.g., Property, Parameter, Condition)."""
        update_attrs(
            self._ATTRS, self._spec, self._run, AttrType, attributes, replace_all, which
        )

    def remove_attributes(
        self,
        AttrType: Type[BaseAttribute],
        attr_names: tuple[str, ...],
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """Removes the attributes with the specified names from the spec or run of the given attribute type (e.g., Property, Parameter, Condition)."""
        remove_attrs(self._ATTRS, self._spec, self._run, AttrType, attr_names, which)

    def prepare_attrs(self):
        """Prepares the attributes for the element based on its template, including conditions, parameters, and properties."""
        self._ATTRS = _validate_temp_keys(self.TEMPLATE)
        if hasattr(self.TEMPLATE, "conditions"):
            for c in self.TEMPLATE.conditions:
                define_attribute(
                    self._ATTRS, template=c[0]
                )  # TODO: look into this weird format from GEMD (attr, bounds)
        if hasattr(self.TEMPLATE, "parameters"):
            for pa in self.TEMPLATE.parameters:
                define_attribute(self._ATTRS, template=pa[0])
        if hasattr(self.TEMPLATE, "properties"):
            for pr in self.TEMPLATE.properties:
                define_attribute(self._ATTRS, template=pr[0])
        finalize_template(self._ATTRS, self.TEMPLATE)

    ############################### PROPERTIES ###############################

    def update_properties(
        self,
        *properties: Property,
        replace_all: bool = False,
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """
        Updates the properties of the run or spec with the specified properties, optionally replacing all existing properties.

        properties: Property
            The properties to change (by name) or add.
        replace_all: bool, default False
            If ``True``, remove any existing properties before adding new ones.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to update the spec, run, or both.
        """

        self.update_attributes(
            AttrType=Property,
            attributes=properties,
            replace_all=replace_all,
            which=which,
        )

    def remove_properties(self, *property_names: str) -> None:  # FIXME: add 'which'
        """
        Remove measured properties from the measurement run or spec by name.

        property_names: str
            The names of properties to remove.

        """

        self.remove_attributes(
            AttrType=Property, attr_names=property_names, which="spec"
        )

    ############################### TAGS ###############################
    def update_tags(
        self,
        *tags: tuple[str, ...],
        replace_all: bool = False,
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """
        Change or add hierarchical tags.

        Each tag is represented by a ``tuple`` of hierarchical ``str`` s. For
        example, ``('Quantum Design', 'MPMS3')``, in that order, describes the
        make and model of a particular measurement instrument.

        When `replace_all` is ``False``, any existing tags that are exactly the
        same as a new tag will not be duplicated. However, a tag that is the
        "child" of an existing tag will not override the "parent" tag. For
        example, it is possible to have all of the following at once:
        ``('Quantum Design', 'DynaCool')``,
        ``('Quantum Design', 'DynaCool', '1')``,
        and ``('Quantum Design', 'DynaCool', '3')``.

        Internally, tag strings will be concatenated with ``'::'`` as
        recommended by the GEMD specification.

        tags: tuple[str]
            tuples representing tags to add. Each tuple should contain the
            components of a tag from most general to most specific.
        replace_all: bool, default False
            If ``True``, remove any existing tags before adding new ones.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to update the spec, run, or both.
        """

        validate_state(which)

        if which in ["spec", "both"]:
            self._set_tags(self._spec, tags, replace_all)

        if which in ["run", "both"]:
            self._set_tags(self._run, tags, replace_all)

    def remove_tags(
        self, *tags: tuple[str, ...], which: SpecOrRunLiteral = "spec"
    ) -> None:
        """Remove tags.

        See `update_tags` for tag format details. Tags are removed by exact
        comparison of the underlying hierarchcal ``str`` s.

        tags: tuple[str]
        ``tuple`` s representing tags to remove.
        which: {'spec', 'run', 'both'}, default 'spec'
        Whether to remove from the spec, run, or both.
        """

        validate_state(which)

        if which in ["spec", "both"]:
            self._remove_tags(self._spec, tags)

        if which in ["run", "both"]:
            self._remove_tags(self._run, tags)

    # TODO: merge into one method?
    @classmethod
    def _set_tags(
        cls,
        spec_or_run: SpecOrRun,
        tags: tuple[tuple[str, ...], ...],
        replace_all: bool = False,
    ) -> None:
        """Set tags for the spec or run."""

        tag_strs = [cls._TAG_SEP.join(tag) for tag in tags]

        if not replace_all:
            existing_tags = [tag for tag in spec_or_run.tags if tag not in tag_strs]
        else:
            existing_tags = []

        spec_or_run.tags = existing_tags + tag_strs

    @classmethod
    def _remove_tags(
        cls, spec_or_run: SpecOrRun, tags: tuple[tuple[str, ...], ...]
    ) -> None:
        """Remove tags from the spec or run."""

        tag_strs = [cls._TAG_SEP.join(tag) for tag in tags]
        spec_or_run.tags = [tag for tag in spec_or_run.tags if tag not in tag_strs]

    def get_tags_dict(self):
        """Get a ``dict`` representing the hierarchical tags."""

        tags_dict = {"spec": {}, "run": {}}

        self._build_tags_dict(self._spec.tags, tags_dict["spec"], self._TAG_SEP)
        self._build_tags_dict(self._run.tags, tags_dict["run"], self._TAG_SEP)

        return tags_dict

    ############################### FILE LINKS ###############################
    def update_filelinks(
        self,
        *filelinks: FileLink,
        replace_all: bool = False,
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """
        Change or add file links.

        filelinks: FileLink
        The file links to change or add.
        replace_all: bool, default False
        If ``True``, remove any existing file links before adding new ones.
        which: {'spec', 'run', 'both'}, default 'spec'
        Whether to update the spec, run, or both.
        """

        validate_state(which)

        supplied_links = {self._link_str(link): link for link in filelinks}

        if which in ["spec", "both"]:
            self._set_filelinks(self._spec, supplied_links, replace_all)

        if which in ["run", "both"]:
            self._set_filelinks(self._run, supplied_links, replace_all)

    @classmethod
    def _set_filelinks(
        cls,
        spec_or_run: SpecOrRun,
        supplied_links: dict[str, FileLink],
        replace_all: bool = False,
    ) -> None:
        """Set links for the spec or run."""

        existing_links = (
            {}
            if replace_all
            else {cls._link_str(link): link for link in spec_or_run.file_links}
        )

        spec_or_run.file_links = {**existing_links, **supplied_links}.values()

    def remove_filelinks(
        self, *filelinks: FileLink, which: SpecOrRunLiteral = "spec"
    ) -> None:
        """Remove file links.

        filelinks: tuple[str]
            The file links to remove by comparison of the underlying url and
            filename.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to remove from the spec, run, or both.
        """

        validate_state(which)

        if which in ["spec", "both"]:
            self._remove_filelinks(self._spec, filelinks)

        if which in ["run", "both"]:
            self._remove_filelinks(self._run, filelinks)

    @classmethod
    def _remove_filelinks(
        cls, spec_or_run: SpecOrRun, filelinks: tuple[FileLink]
    ) -> None:
        """Remove tags from the spec or run."""

        filelink_strs = [cls._link_str(link) for link in filelinks]

        spec_or_run.file_links = [
            link
            for link in spec_or_run.file_links
            if cls._link_str(link) not in filelink_strs
        ]

    @staticmethod
    def _link_str(link: FileLink) -> str:
        """
        Return a str representation of a ``FileLink`` based on its ``filename`` and url``.
        """
        # TODO: add conversion to standard file path or https
        return f'{link.filename}{"/" if link.filename.endswith("/") else ","}{link.url}'

    def get_filelinks_dict(self):
        """
        Get string representations of the file links.

        filelinks_dict: FileLinksDict
            Strings representing the file links of the spec and run.
        """

        filelinks_dict = {}

        filelinks_dict["spec"] = tuple(
            self._link_str(link) for link in self._spec.file_links
        )
        filelinks_dict["run"] = tuple(
            self._link_str(link) for link in self._run.file_links
        )

        return filelinks_dict
