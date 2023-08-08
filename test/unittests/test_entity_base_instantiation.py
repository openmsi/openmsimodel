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
    ct = ConditionTemplate(
        "location",
        uids={"gen": "uid_2"},
        bounds=CategoricalBounds(["Purification Tube Furnace", "X-Ray Panel"]),
        description="none",
    )
    # TODO: test define attributes when the same attribute is repassed

    def test_base_node_initialization(self):
        """testing initialization of BaseNode object"""
        with self.assertRaises(
            TypeError
        ):  # abstract class can't instantiate on its own
            b = BaseNode("base")

    def test_incomplete_initializing(self):
        """testing initializing with incomplete or erroneous classes"""

        # initializing with an incomplete subclassing
        with self.assertRaises(AttributeError):
            i = incompleteSubclass("incomplete")

        # needs a template, either passed or defined in subclass
        with self.assertRaises(AttributeError):
            p = Process("process")

        # initializing with wrong subclasses
        for i in range(2, 4):  # TODO: fix testing for i==1
            with self.assertRaises(TypeError):
                module = str(
                    "data.subclassing.erroneous_subclass_{}.erroneousSubclass{}".format(
                        i, i
                    )
                )
                importlib.import_module(module)
        for i in range(5, 8):
            with self.assertRaises(NameError):
                module = str(
                    "data.subclassing.erroneous_subclass_{}.erroneousSubclass{}".format(
                        i, i
                    )
                )
                importlib.import_module(module)

        # initializing by passing a template WITHOUT attribute templates + actual attributes
        with self.assertRaises(KeyError):
            p = Process(
                "process",
                template=ProcessTemplate(
                    "process template",
                    conditions=[],
                ),
                conditions=[
                    Condition(
                        "location",
                        value=NominalCategorical("X-Ray Panel"),
                        template=self.ct,
                    )
                ],
            )

        # initializing with wrong template type
        with self.assertRaises(TypeError):
            p = Process(
                "process",
                template=MaterialTemplate(
                    "material template",
                ),
            )

        # initializing with attribute template that isn't accepted (i.e., material CANT have parameters)
        with self.assertRaises(TypeError):
            p = Material(
                "material",
                template=MaterialTemplate(
                    "material template",
                ),
                parameters=[
                    Parameter(
                        "location",
                        value=NominalCategorical("Choice 1"),
                        template=ParameterTemplate(
                            "t", bounds=CategoricalBounds(["Choice 1"])
                        ),
                    )
                ],
            )

        # initializing with an assigned 'auto' uid
        pt = ProcessTemplate(
            "process template", uids={"gen": "uid_3"}, conditions=[self.ct]
        )
        with self.assertRaises(KeyError):
            p = Process("process", template=pt)

    def test_all_initializations(self):
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
        t = ProcessTemplate("process template", uids={"gen": "uid_1"})
        p = Process("process", template=t)
        self.assertIn("auto", p.TEMPLATE.uids.keys())
        self.assertEquals(t.uids["auto"], p.TEMPLATE.uids["auto"])
        self.assertEquals(t.uids["gen"], "uid_1")
        del t
        del p

        # initializing by subclassing and passing a template
        a = ArcMeltingExample(
            "arc melting",
            template=ProcessTemplate(
                "process template",
            ),
        )
        del a

        # initializing by passing a template with attribute templates
        pt = ProcessTemplate(
            "process template", uids={"gen": "uid_3"}, conditions=[self.ct]
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
