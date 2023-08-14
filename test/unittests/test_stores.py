# imports
import pkg_resources, subprocess, unittest, sys, importlib

sys.path.insert(0, "..")
# from data.subclassing.incomplete_subclass import incompleteSubclass
# from data.subclassing.erroneous_subclass_1 import erroneousSubclass1
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

    def test_stores(self):
        """testing initialization of all types of BaseNode object"""

        # initializing by subclassing
        a = ArcMeltingExample("arc melting")
        self.assertIn("auto", a.TEMPLATE.uids.keys())
        self.assertEquals(len(a.TEMPLATE.parameters), 5)
        self.assertEquals(len(a._ATTRS["parameters"]), 5)
        self.assertEquals(len(a.run.parameters), 0)
        self.assertEquals(
            len(a.spec.parameters), 2
        )  # 2/5 ParameterTemplates have default values, that get assigned to specs
        del a

        # initializing by passing a template
        name = "1st process template"
        t = ProcessTemplate(name, uids={"gen": "uid_1"})
        p = Process("process", template=t)
        self.assertIn("auto", p.TEMPLATE.uids.keys())
        self.assertEquals(t.uids["auto"], p.TEMPLATE.uids["auto"])
        self.assertEquals(t.uids["gen"], "uid_1")
        del t
        del p

        # initializing by subclassing and passing a template
        def instantiate(template_name):
            a = ArcMeltingExample(
                "arc melting",
                template=ProcessTemplate(
                    template_name,
                ),
            )

        with self.assertRaises(NameError):
            instantiate(name)
        instantiate("2nd process template")

        # initializing by passing a template with attribute templates
        pt = ProcessTemplate(
            "3rd process template", uids={"gen": "uid_3"}, conditions=[self.ct]
        )
        p = Process("process", template=pt)
        self.assertEquals(pt.uids["auto"], p.TEMPLATE.uids["auto"])
        self.assertEquals(
            self.ct.uids["auto"], p.TEMPLATE.conditions[0][0].uids["auto"]
        )
        self.assertEquals(len(p.TEMPLATE.conditions), 1)
        del pt
        del p

        # initializing by passing a template with attribute templates + actual attributes
        # a)
        p = Process(
            "process",
            template=ProcessTemplate(
                "4th process template",
                conditions=[self.ct],
            ),
            conditions=[
                Condition(
                    "location",
                    value=NominalCategorical("X-Ray Panel"),
                    template=self.ct,
                )
            ],
        )
        self.assertEquals(
            self.ct.uids["auto"], p.spec.conditions[0].template.uids["auto"]
        )
        self.assertEquals(len(p.TEMPLATE.conditions), 1)
        del p

        p = Process(
            "process",
            template=ProcessTemplate(
                "process template",
                conditions=[self.ct],
            ),
            conditions=[
                Condition(
                    "location",
                    value=NominalCategorical("X-Ray Panel"),
                    template=self.ct,
                )
            ],
            state="run",
        )
        self.assertEquals(
            self.ct.uids["auto"], p.run.conditions[0].template.uids["auto"]
        )
        del p

        p = Process(
            "process",
            template=ProcessTemplate(
                "process template",
                conditions=[self.ct],
            ),
            conditions=[
                Condition(
                    "location",
                    value=NominalCategorical("X-Ray Panel"),
                    template=self.ct,
                )
            ],
            state="both",
        )

        self.assertEquals(
            self.ct.uids["auto"], p.spec.conditions[0].template.uids["auto"]
        )
        self.assertEquals(
            self.ct.uids["auto"], p.run.conditions[0].template.uids["auto"]
        )

        del p

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
