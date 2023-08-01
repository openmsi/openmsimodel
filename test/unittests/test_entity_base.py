# imports
import pkg_resources, subprocess, unittest
from openmsimodel.entity.base import (
    BaseNode,
    Process,
    Measurement,
    Ingredient,
    Material,
)
from openmsimodel.entity import ArcMelting

from gemd import (
    ProcessRun,
    ProcessSpec,
    ProcessTemplate,
    Parameter,
    NominalCategorical,
    NominalReal,
)
from gemd.json import GEMDJson
from gemd.entity.util import make_instance


class TestEntityBaseNode(unittest.TestCase):
    def test_initialization(self):
        """testing initialization of BaseNode object"""
        with self.assertRaises(TypeError):  # can't instantiate on its own
            b = BaseNode("base")

    def test_all_initializations(self):
        """testing initialization of all types of BaseNode object"""
        with self.assertRaises(AttributeError):
            p = Process("process")

    def test_from_spec_or_run(self):
        # without template
        with self.assertRaises(AttributeError):
            p = Process.from_spec_or_run(
                "process",
                notes=["adding notes to a process"],
                spec=ProcessSpec("process spec", template=None, parameters=[]),
                run=ProcessRun("process run", parameters=[]),
            )

        # with template
        with self.assertRaises(AttributeError):
            p = Process.from_spec_or_run(
                "process",
                notes=["adding notes to a process"],
                spec=ProcessSpec(
                    "process spec",
                    template=ProcessTemplate(
                        "process template",
                        description="Template of process",
                        conditions=[],
                        parameters=[],
                    ),
                    parameters=[],
                ),
                run=ProcessRun("process run", spec=None, parameters=[]),  # test
            )

        # with pre existing thing
        encoder = GEMDJson()
        t = ProcessTemplate(
            "process template",
            description="Template of process",
            conditions=[],
            parameters=[],
        )
        value = "900-950"
        s = ProcessSpec(
            "process spec",
            template=t,
            parameters=[
                Parameter(
                    "Argon Pressure",
                    value=NominalCategorical(value),
                    origin="specified",
                )
            ],
        )
        r = make_instance(s)
        encoder.thin_dumps(r)

        p = ArcMelting.from_spec_or_run(
            "process", notes=["adding notes to process"], spec=s
        )
        self.assertEquals(p.spec.uids["auto"], s.uids["auto"])
        self.assertEquals(p.spec.parameters[2].value.category, value)

        p = ArcMelting.from_spec_or_run(
            "process", notes=["adding notes to process"], run=r
        )
        self.assertEquals(p.run.uids["auto"], r.uids["auto"])

        p = ArcMelting.from_spec_or_run(
            "process", notes=["adding notes to process"], spec=s, run=r
        )
        self.assertEquals(p.spec, s)
        self.assertEquals(p.spec.uids["auto"], s.uids["auto"])
        self.assertEquals(p.run.uids["auto"], r.uids["auto"])
        self.assertEquals(p.spec.parameters[2].value.category, value)

    def test_from_spec_or_run_2(self):
        pass

    def testt(self):
        p = ArcMelting("arc melting")
        p._update_attributes(
            AttrType=Parameter,
            attributes=(
                Parameter(
                    "Argon Pressure",
                    value=NominalCategorical(value),
                    origin="specified",
                ),
                Parameter(
                    "Initial Purging Times",
                    value=NominalReal(1, "hour"),
                    origin="specified",
                ),
            ),
        )
