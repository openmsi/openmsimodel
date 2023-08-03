# imports
import pkg_resources, subprocess, unittest, sys, importlib

sys.path.insert(0, "..")
from data.subclassing.incomplete_subclass import incompleteSubclass
from data.subclassing.erroneous_subclass_1 import erroneousSubclass1
from data.subclassing.arcmelting_example_subclass import ArcMeltingExample

from openmsimodel.entity.base import (
    BaseNode,
    Process,
    Measurement,
    Ingredient,
    Material,
)

from gemd import (
    NominalCategorical,
    NominalReal,
    CategoricalBounds,
    ProcessRun,
    ProcessSpec,
    ProcessTemplate,
    MaterialTemplate,
    MeasurementTemplate,
    Parameter,
    ParameterTemplate,
    Property,
    PropertyTemplate,
    Condition,
    ConditionTemplate,
)
from gemd.json import GEMDJson
from gemd.entity.util import make_instance


class TestEntityBaseNode(unittest.TestCase):
    # TODO: test define attributes when the same attribute is repassed
    def test_same_spec_and_template(self):
        # initializing and making sure specs are the same
        a = ArcMeltingExample(
            "arc melting",
            template=ProcessTemplate(
                "process template",
            ),
        )

        a_2 = ArcMeltingExample(
            "arc melting 2",
            template=ProcessTemplate(
                "process template",
            ),
        )
        # self.assertEqual(a.spec.uids["auto"], a_2.spec.uids["auto"])
        # self.assertEqual(a.TEMPLATE.uids["auto"], a_2.TEMPLATE.uids["auto"])

    # def test_from_spec_or_run(self):
    #     # without template
    #     with self.assertRaises(AttributeError):
    #         p = Process.from_spec_or_run(
    #             "process",
    #             notes=["adding notes to a process"],
    #             spec=ProcessSpec("process spec", template=None, parameters=[]),
    #             run=ProcessRun("process run", parameters=[]),
    #         )

    #     # with template
    #     with self.assertRaises(AttributeError):
    #         p = Process.from_spec_or_run(
    #             "process",
    #             notes=["adding notes to a process"],
    #             spec=ProcessSpec(
    #                 "process spec",
    #                 template=ProcessTemplate(
    #                     "process template",
    #                     description="Template of process",
    #                     conditions=[],
    #                     parameters=[],
    #                 ),
    #                 parameters=[],
    #             ),
    #             run=ProcessRun("process run", spec=None, parameters=[]),  # test
    #         )

    #     # with pre existing thing
    #     encoder = GEMDJson()
    #     t = ProcessTemplate(
    #         "process template",
    #         description="Template of process",
    #         conditions=[],
    #         parameters=[],
    #     )
    #     value = "900-950"
    #     s = ProcessSpec(
    #         "process spec",
    #         template=t,
    #         parameters=[
    #             Parameter(
    #                 "Argon Pressure",
    #                 value=NominalCategorical(value),
    #                 origin="specified",
    #             )
    #         ],
    #     )
    #     r = make_instance(s)
    #     encoder.thin_dumps(r)

    #     p = ArcMeltingExample.from_spec_or_run(
    #         "process", notes=["adding notes to process"], spec=s
    #     )
    #     self.assertEquals(p.spec.uids["auto"], s.uids["auto"])
    #     self.assertEquals(p.spec.parameters[2].value.category, value)

    #     p = ArcMeltingExample.from_spec_or_run(
    #         "process", notes=["adding notes to process"], run=r
    #     )
    #     self.assertEquals(p.run.uids["auto"], r.uids["auto"])

    #     p = ArcMeltingExample.from_spec_or_run(
    #         "process", notes=["adding notes to process"], spec=s, run=r
    #     )
    #     self.assertEquals(p.spec, s)
    #     self.assertEquals(p.spec.uids["auto"], s.uids["auto"])
    #     self.assertEquals(p.run.uids["auto"], r.uids["auto"])
    #     self.assertEquals(p.spec.parameters[2].value.category, value)

    # def test_from_spec_or_run_2(self):
    #     pass

    # def testt(self):
    #     p = ArcMeltingExample("arc melting")
    #     value = "900-950"
    #     p._update_attributes(
    #         AttrType=Parameter,
    #         attributes=(
    #             Parameter(
    #                 "Argon Pressure",
    #                 value=NominalCategorical(value),
    #                 origin="specified",
    #             ),
    #             Parameter(
    #                 "Initial Purging Times",
    #                 value=NominalReal(1, "hour"),
    #                 origin="specified",
    #             ),
    #         ),
    #     )
