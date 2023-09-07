"""Base class for classes containing GEMD templates and objects."""

import os, warnings
from abc import ABC, abstractmethod
from typing import ClassVar, Type, Optional

from gemd import FileLink
from gemd.entity.attribute.base_attribute import BaseAttribute
from gemd.entity.template.base_template import BaseTemplate
from gemd.entity.util import make_instance

# from gemd.util.impl import set_uuids
from openmsimodel.entity.impl import assign_uuid

from openmsimodel.utilities.typing import (
    ObjTemplate,
    Spec,
    Run,
    SpecOrRun,
    SpecOrRunLiteral,
    # TagsDict,
    # FileLinksDict,
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
import openmsimodel.stores.gemd_template_store as gemd_template_store

from pydantic import BaseModel, PrivateAttr, Extra, Field
import sys

sys.path.append("/srv/hemi01-j01/gemd-schema")
from gemd_schema.attribute_template_basemodel import AttributeTemplate
from gemd_schema.object_template_basemodel import ObjectTemplate

__all__ = ["BaseElement"]


class BaseElement(ABC, BaseModel):
    """
    Base class for materials, processes, and measurements.

    ``BaseElement`` 's are thin wrappers for GEMD entities. One ``BaseElement`` contains
    a template, spec, and run for the same kind of entity (``Material``,
    ``Process``, or ``Measurement``) and helps to create, update, link, and
    output these.

    Note that `name` is the GEMD name given to the spec and run. The template
    name is the name of the subclass.

    To subclass:

    1. Instantiate ``_TEMPLATE`` as follows:
    ``_TEMPLATE: ClassVar[ObjTemplate] = ObjTemplate(name=__name__)``,
    replacing ``ObjTemplate`` with one of ``MaterialTemplate``,
    ``ProcessTemplate``, or ``MeasurementTemplate``.

    2. Instantiate ``_ATTRS`` as follows:
    ``_ATTRS``: ClassVar[AttrsDict] = _validate_temp_keys(_TEMPLATE)

    3. Add conditions, parameters, and/or properties using
    ``define_attribute(_ATTRS, ...)`` from the ``qf_gemd.base.attributes``
    module.

    4. Call ``finalize_template(_ATTRS, _TEMPLATE)``, found in the
    ``qf_gemd.base.attributes`` module, to add attributes to ``_TEMPLATE``.

    5. Follow any additional subclass directions.
    """

    class Config:
        arbitrary_types_allowed = True

    name: str

    _TempType: ClassVar[Type[ObjTemplate]]
    _SpecType: ClassVar[Type[Spec]]
    _RunType: ClassVar[Type[Run]]
    logger: ClassVar[Logger] = Logger()
    _TAG_SEP: ClassVar[str] = "::"

    # TEMPLATE: BaseTemplate = Field(..., title="some")
    TEMPLATE: ObjectTemplate
    _ATTRS: PrivateAttr(AttrsDict) = {}
    _TEMPLATE_WRAPPER: dict = PrivateAttr({})

    _spec: Spec = None
    _run: Run = None

    # TODO: remove and put somewhere

    def __init__(
        self,
        name: str,
        *,
        template: ClassVar[
            ObjTemplate
        ] = None,  # TODO: triple check with abc's hastemplate
        notes: Optional[str] = None,
    ) -> None:
        # BaseModel.__init__(self, **{"name": name})
        _TEMPLATE_WRAPPER = {}

        has_template = hasattr(self, "_TEMPLATE")

        if not has_template and not template:
            raise AttributeError(
                f"_TEMPLATE is not defined. Assign to 'template' parameter an instance of either {ObjTemplate.__dict__['__args__']},\n OR create a new subclass with a defined _TEMPLATE attribute."
            )

        if template:
            if has_template:
                warnings.warn(
                    f"Found template '{self._TEMPLATE.name}', but '{template.name}' will be used instead.",
                    ResourceWarning,
                )
            _TEMPLATE = template
            if hasattr(_TEMPLATE, "uids") and (
                ("persistent_id" in _TEMPLATE.uids.keys())
                or ("auto" in _TEMPLATE.uids.keys())
            ):
                raise KeyError(
                    f'the "auto" and "persistent_id" uid keys are reserved. Use another key. '
                )

            # TODO: Extend (or sync with external func that returns a dict for runs/specs

        # TODO: change from file when supporting file links
        for i, store in enumerate(gemd_template_store.all_template_stores.values()):
            _TEMPLATE_WRAPPER[store.id] = store.register_new_template(
                _TEMPLATE,
                from_file=False,
                from_store=False,
                from_memory=bool(template),
                from_subclass=bool(has_template and not template),
            )
            if i == 0:  # first one is the the designated store for accessing template
                designated_store_id = store.id
                _TEMPLATE = _TEMPLATE_WRAPPER[designated_store_id].template

        if template:
            _ATTRS = self.prepare_attrs(_TEMPLATE)
            # FIXME: call finalize here?

        for i, store in enumerate(gemd_template_store.all_template_stores.values()):
            for _attr_type in _ATTRS.keys():
                for _attr in _ATTRS[_attr_type].values():
                    gemd_template_store.all_template_stores[
                        store.id
                    ].register_new_template(_attr["obj"])

        _spec = self._SpecType(name=name, notes=notes, template=_TEMPLATE)
        assign_uuid(_spec, "auto")
        # if spec the same as in store, use the one in store
        # if not, use the one instantiated from template
        # sce 1: diff template but same name
        _run = make_instance(_spec)
        assign_uuid(_run, "auto")
        # _TEMPLATE = {
        #     "type": "material_template",
        #     "name": "na",
        #     "uids": {"auto": "0de7d6af-7a34-4bb1-8575-88ff6125f9bb"},
        #     "tags": [],
        #     "file_links": {"filename": "", "url": ""},
        #     "notes": "fe",
        # }
        BaseModel.__init__(
            self,
            **{
                "name": name,
                "TEMPLATE": _TEMPLATE,
                "_run": _run,
                "_spec": _spec,
                "_ATTRS": _ATTRS,
            },
        )
        print("here")

    @property
    @abstractmethod
    def spec(self) -> Spec:
        """The underlying GEMD spec."""

    @property
    @abstractmethod
    def run(self) -> Run:
        """The underlying GEMD run."""

    @classmethod
    @abstractmethod
    def from_spec_or_run(
        cls,
        name: str,
        *,
        notes: Optional[str] = None,
        spec: Spec = None,
        run: Run = None,
    ) -> "BaseElement":
        """
        Instantiate a `BaseElement` from a spec or run with appropriate validation.

        Note that the spec's and run's name and notes will be set to `name` and
        `notes`, the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        """

    ############################### ATTRIBUTES ###############################

    def _update_attributes(
        self,
        AttrType: Type[BaseAttribute],
        attributes: tuple[BaseAttribute],
        replace_all: bool = False,
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """Update attributes and link attribute templates."""

        update_attrs(
            self._ATTRS, self._spec, self._run, AttrType, attributes, replace_all, which
        )

    def _remove_attributes(
        self,
        AttrType: Type[BaseAttribute],
        attr_names: tuple[str, ...],
        which: SpecOrRunLiteral = "spec",
    ) -> None:
        """Remove attributes by name."""

        remove_attrs(self._ATTRS, self._spec, self._run, AttrType, attr_names, which)

    def prepare_attrs(self, template):
        _ATTRS = _validate_temp_keys(template)
        if hasattr(template, "conditions"):
            for c in template.conditions:
                define_attribute(
                    _ATTRS, template=c[0]
                )  # TODO: look into this weird format from GEMD (attr, bounds)
        if hasattr(template, "parameters"):
            for p in template.parameters:
                define_attribute(_ATTRS, template=p[0])
        if hasattr(template, "properties"):
            for p in template.properties:
                define_attribute(_ATTRS, template=p[0])
        return _ATTRS
        # finalize_template(self._ATTRS, self._TEMPLATE)

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

    @staticmethod
    def _build_tags_dict(tags: list[str], parent_dict: dict, tag_sep: str) -> None:
        """Build a spec or run hierarchical tags ``dict``."""

        for tag_str in tags:
            tag_tup = tag_str.split(tag_sep)
            parent = parent_dict
            for component in tag_tup:
                if component not in parent:
                    parent[component] = {}
                parent = parent[component]

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

    # TODO: add a 'update_spec' function to != the 1:1 / template:spec duality

    # @abstractmethod
    # def to_form(self) -> str:
    #     """Return a ``str`` specifying how to create a web form for this node."""

    # def thin_dumps(self, encoder, destination):
    #     for obj in [self._spec, self._run]:
    #         encoder.thin_dumps(obj,indent=3) # trigger uids assignment
    #         fn = '_'.join([obj.__class__.__name__, obj.name,obj.uids['auto']])
    #         with open(os.path.join(destination, fn),'w') as fp:
    #             fp.write(encoder.thin_dumps(obj,indent=3))

    def thin_dumps(self, encoder, destination):
        self.dump_loop(encoder.thin_dumps, destination)

    def dumps(self, encoder, destination):
        self.dump_loop(encoder.dumps, destination)

    def dump_loop(self, encoder_func, destination):
        for obj in [self._spec, self._run]:
            encoder_func(obj, indent=3)  # trigger uids assignment
            fn = "_".join([obj.__class__.__name__, obj.name, obj.uids["auto"]])
            with open(os.path.join(destination, fn), "w") as fp:
                fp.write(encoder_func(obj, indent=3))
