"""Base class for classes containing GEMD templates and objects."""

from abc import ABC, abstractmethod
from typing import ClassVar, Type, Optional

from gemd import FileLink
from gemd.entity.attribute.base_attribute import BaseAttribute
from gemd.entity.util import make_instance

from .typing import Temp, Spec, Run, SpecOrRun, SpecRunLiteral, TagsDict, FileLinksDict
from .attributes import AttrsDict, validate_which, update_attrs, remove_attrs

import os

__all__ = ["BaseNode"]


class BaseNode(ABC):
    """
    Base class for materials, processes, and measurements.

    ``BaseNode``s are thin wrappers for GEMD entities. One ``BaseNode`` contains
    a template, spec, and run for the same kind of entity (``Material``,
    ``Process``, or ``Measurement``) and helps to create, update, link, and
    output these.

    Note that `name` is the GEMD name given to the spec and run. The template
    name is the name of the subclass.

    The `to_form` abstract method could be implemented to instruct a webpage
    how to create form elements and validation based on the template.

    To subclass:

    1. Instantiate ``TEMPLATE`` as follows:
    ``TEMPLATE: ClassVar[Template] = Template(name=__name__)``,
    replacing ``Template`` with one of ``MaterialTemplate``,
    ``ProcessTemplate``, or ``MeasurementTemplate``.

    2. Instantiate ``_ATTRS`` as follows:
    ``_ATTRS: ClassVar[AttrsDict] = {'conditions': {}, 'parameters': {}, 'properties': {}}``.
    However, only include the relevant keys (e.g., exclude ``'properties'`` for a ``Process``
    subclass).

    3. Add conditions, parameters, and/or properties using
    ``define_attribute(_ATTRS, ...)`` from the ``qf_gemd.base.attributes``
    module.

    4. Call ``finalize_template(_ATTRS, TEMPLATE)``, found in the
    ``qf_gemd.base.attributes`` module, to add attributes to ``TEMPLATE``.

    5. Follow any additional subclass directions.
    """

    _TempType: ClassVar[Type[Temp]]
    _SpecType: ClassVar[Type[Spec]]
    _RunType: ClassVar[Type[Run]]

    TEMPLATE: ClassVar[Temp]

    _ATTRS: ClassVar[AttrsDict]

    _TAG_SEP: ClassVar[str] = "::"

    def __init__(self, name: str, *, notes: Optional[str] = None) -> None:
        super().__init__()
        self._spec: Spec = self._SpecType(
            name=name, notes=notes, template=self.TEMPLATE
        )
        self._run: Run = make_instance(self._spec)

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
    ) -> "BaseNode":
        """
        Instantiate a `BaseNode` from a spec or run with appropriate validation.

        Note that the spec's and run's name and notes will be set to `name` and
        `notes`, the spec's template will be set to the class template,
        and the run's spec will be set to this spec.
        """

    def _update_attributes(
        self,
        AttrType: Type[BaseAttribute],
        attributes: tuple[BaseAttribute],
        replace_all: bool = False,
        which: SpecRunLiteral = "spec",
    ) -> None:
        """Update attributes and link attribute templates."""

        update_attrs(
            self._ATTRS, self._spec, self._run, AttrType, attributes, replace_all, which
        )

    def _remove_attributes(
        self,
        AttrType: Type[BaseAttribute],
        attr_names: tuple[str, ...],
        which: SpecRunLiteral = "spec",
    ) -> None:
        """Remove attributes by name."""

        remove_attrs(self._ATTRS, self._spec, self._run, AttrType, attr_names, which)

    def get_tags_dict(self) -> TagsDict:
        """Get a ``dict`` representing the hierarchical tags."""

        tags_dict = {"spec": {}, "run": {}}

        self._build_tags_dict(self._spec.tags, tags_dict["spec"], self._TAG_SEP)
        self._build_tags_dict(self._run.tags, tags_dict["run"], self._TAG_SEP)

        return tags_dict

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

    def update_tags(
        self,
        *tags: tuple[str, ...],
        replace_all: bool = False,
        which: SpecRunLiteral = "spec",
    ) -> None:
        """
        Change or add hierarchical tags.

        Each tag is represented by a ``tuple`` of hierarchical ``str``s. For
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

        Parameters
        ----------
        *tags: tuple[str]
            ``tuple``s representing tags to add. Each tuple should contain the
            components of a tag from most general to most specific.
        replace_all: bool, default False
            If ``True``, remove any existing tags before adding new ones.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to update the spec, run, or both.
        """

        validate_which(which)

        if which in ["spec", "both"]:
            self._set_tags(self._spec, tags, replace_all)

        if which in ["run", "both"]:
            self._set_tags(self._run, tags, replace_all)

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

    def remove_tags(
        self, *tags: tuple[str, ...], which: SpecRunLiteral = "spec"
    ) -> None:
        """Remove tags.

        See `update_tags` for tag format details. Tags are removed by exact
        comparison of the underlying hierarchcal ``str``s.

        Parameters
        ----------
        *tags: tuple[str]
            ``tuple``s representing tags to remove.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to remove from the spec, run, or both.
        """

        validate_which(which)

        if which in ["spec", "both"]:
            self._remove_tags(self._spec, tags)

        if which in ["run", "both"]:
            self._remove_tags(self._run, tags)

    @classmethod
    def _remove_tags(
        cls, spec_or_run: SpecOrRun, tags: tuple[tuple[str, ...], ...]
    ) -> None:
        """Remove tags from the spec or run."""

        tag_strs = [cls._TAG_SEP.join(tag) for tag in tags]
        spec_or_run.tags = [tag for tag in spec_or_run.tags if tag not in tag_strs]

    def get_filelinks_dict(self) -> FileLinksDict:
        """
        Get string representations of the file links.

        Returns
        -------
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

    def update_filelinks(
        self,
        *filelinks: FileLink,
        replace_all: bool = False,
        which: SpecRunLiteral = "spec",
    ) -> None:
        """
        Change or add file links.

        Parameters
        ----------
        *filelinks: FileLink
            The file links to change or add.
        replace_all: bool, default False
            If ``True``, remove any existing file links before adding new ones.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to update the spec, run, or both.
        """

        validate_which(which)

        supplied_links = {self._link_str(link): link for link in filelinks}

        if which in ["spec", "both"]:
            self._set_filelinks(self._spec, supplied_links, replace_all)

        if which in ["run", "both"]:
            self._set_filelinks(self._run, supplied_links, replace_all)

    @staticmethod
    def _link_str(link: FileLink) -> str:
        """
        Return a str representation of a ``FileLink`` based on its ``filename`` and url``.
        """
        # TODO: add conversion to standard file path or https
        return f'{link.filename}{"/" if link.filename.endswith("/") else ","}{link.url}'

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
        self, *filelinks: FileLink, which: SpecRunLiteral = "spec"
    ) -> None:
        """Remove file links.

        Parameters
        ----------
        *filelinks: tuple[str]
            The file links to remove by comparison of the underlying url and
            filename.
        which: {'spec', 'run', 'both'}, default 'spec'
            Whether to remove from the spec, run, or both.
        """

        validate_which(which)

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

    @abstractmethod
    def to_form(self) -> str:
        """Return a ``str`` specifying how to create a web form for this node."""

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
