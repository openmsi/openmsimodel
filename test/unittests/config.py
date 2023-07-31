# imports
import os, pathlib
from openmsistream.utilities.config import RUN_CONST
from openmsistream.data_file_io.config import RUN_OPT_CONST


class TestRoutineConstants:
    """
    constants used in running tests
    """

    @property
    def TEST_DIR_PATH(self):
        return pathlib.Path(__file__).parent.parent

    @property
    def PACKAGE_ROOT_DIR(self):
        return self.TEST_DIR_PATH.parent / "openmsimodel"

    @property
    def TEST_DATA_DIR_PATH(self):  # path to the test data directory
        return self.TEST_DIR_PATH / "data"

    @property
    def TEST_IDENTIFIER(self):  # uuid identifier of gemd object
        return "ucid9"


TEST_CONST = TestRoutineConstants()
