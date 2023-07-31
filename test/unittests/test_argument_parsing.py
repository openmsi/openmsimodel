import unittest, pathlib, shutil, os
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from config import TEST_CONST


class TestArgumentParsing(unittest.TestCase):
    """
    Class for testing functions in utilities/argument_parsing.py
    """

    def test_my_argument_parser(self):
        """
        testing parser's against existing and non-existing arguments
        """

        parser = OpenMSIModelParser()
        parser.add_arguments(
            "dirpath", "identifier", "add_attributes", "launch_notebook"
        )
        args = [
            os.fspath(TEST_CONST.TEST_DATA_DIR_PATH / "dirpath"),
            "--identifier",
            TEST_CONST.TEST_IDENTIFIER,
            "--launch_notebook",
        ]
        args = parser.parse_args(args=args)
        self.assertEqual(args.identifier, TEST_CONST.TEST_IDENTIFIER)
        self.assertTrue(args.launch_notebook)

        # non-existing arg
        with self.assertRaises(ValueError):
            parser = OpenMSIModelParser()
            parser.add_arguments("never_name_a_command_line_arg_this")
