from pathlib import Path
import os


def is_not_hidden(path):
    return not path.name.startswith(".")


class FolderOrFile:
    """
    class that represents a folder and its elements, or a file.
    It uses recursion to explore and record folder hiearchies that can be exploited
    for modelling. For example, if a team follows a protocol for data storage, naming, etc, using
    folder structures.
    """

    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    # def __init__(self, *args, **kwargs):
    def __init__(self, root, parent_path, is_last):
        """
        this class represents a folder or a file, and is used in a recursive approach to
        build trees, navigate them or display them swiftly.
        :param path: the path to the folder/file to display and build tree from
        :param parent_path: path to the parent folder of current object
        :param is_last: is this the last element in the tree

        """
        self.root = Path(str(root))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        """
        displays the name of the folder or file
        """
        if self.root.is_dir():
            return self.root.name + "/"
        return self.root.name

    @classmethod
    def make_tree(self, cls, root, parent=None, is_last=False, criteria=None):  # FIXME
        """
        powerful function that builds trees recursively.
        It passes the current item, displayable_root, as the 'parent' parameters to its children to navigate down the tree.
        It stops the recursion when there are no more children, or is_last=False.
        It can use the criteria to filter the children
        :param root: the path to the folder/file to display and build tree from
        :param parent: parent object of current item
        :param is_last: is this the last element in the tree
        :criteria: a function that takes a path and returns True if the path should be included in the tree
        """
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        # if directory, list of elements in lower case
        children = sorted(
            list(path for path in root.iterdir() if criteria(path)),
            key=lambda s: str(s).lower(),
        )

        count = 1  # used to track nb of elements, not DEPTH
        for path in children:
            is_last = count == len(children)
            if path.is_dir():  # directory vs file
                yield from cls.make_tree(
                    cls=cls,
                    root=path,
                    parent=displayable_root,
                    is_last=is_last,
                    criteria=criteria,
                )
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    def displayable(self):
        """
        functions that returns a nicely formatted string that display the tree items and hierarchy.
        It navigates up to the tree in a loop by reading the parent attribute one at a time, and
        extracting its displayname.
        Finally, it renders all the display names (which are reversed to be in the correct order).
        """
        if self.parent is None:
            return self.displayname

        # distinguishes the printing of tree symbols from the last one and the rests
        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        # attaches correct tree symbols with actual file/folder names
        parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

        parent = self.parent
        while (
            parent and parent.parent is not None
        ):  # TODO: update because empty folders are considered as None
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        # because children are appended first and parents last, a reversal is necessary
        return "".join(reversed(parts))
