# imports
import pkg_resources, subprocess, unittest, sys, importlib, warnings
from pathlib import Path

sys.path.insert(0, "..")
from data.subclassing.incomplete_subclass import incompleteSubclass
from data.subclassing.erroneous_subclass_1 import erroneousSubclass1  # FIXME ?
from data.subclassing.arcmelting import ArcMelting

# setting up stores for testing
from openmsimodel.stores.gemd_template_store import GEMDTemplateStore

test_root = Path(__file__).parent.parent / "data/stores/templates"
test_template_store = GEMDTemplateStore(id="test", load_all_files=False)
test_template_store.root = test_root
test_template_store.initialize_store()
test_template_store.register_all_templates_from_store()
# setting global store = test store for testing
import openmsimodel.stores.gemd_template_store as gemd_template_store

gemd_template_store.all_template_stores = {"test": test_template_store}

from openmsimodel.entity.base.base_element import BaseElement
from openmsimodel.entity.base.process import Process
from openmsimodel.entity.base.material import Material
from openmsimodel.entity.base.ingredient import Ingredient
from openmsimodel.entity.base.measurement import Measurement

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


class TestEntityBaseElement(unittest.TestCase):
    ct = ConditionTemplate(
        "location",
        uids={"gen": "uid_2"},
        bounds=CategoricalBounds(["Purification Tube Furnace", "X-Ray Panel"]),
        description="none",
    )
    # TODO: test define attributes when the same attribute is repassed

    def test_base_node_initialization(self):
        """testing initialization of BaseElement object"""
        with self.assertRaises(
            TypeError
        ):  # abstract class can't instantiate on its own
            b = BaseElement("base")

    def test_incomplete_initializations(self):
        """testing initializing with incomplete or erroneous classes"""

        # initializing with an incomplete subclassing
        with self.assertRaises(AttributeError):
            i = incompleteSubclass("incomplete")

        # needs a template, either passed or defined in subclass
        with self.assertRaises(AttributeError):
            p = Process("process")

    def test_wrong_initializations(self):
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
                    conditions=[],  # no att template...
                ),
                conditions=[  # ... but still, atts are passed
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

        # initializing with an assigned 'auto' or 'persistent_id' uid
        pt = ProcessTemplate(
            "process template", uids={"auto": "uid_3"}, conditions=[self.ct]
        )
        with self.assertRaises(KeyError):
            p = Process("process", template=pt)

        pt = ProcessTemplate(
            "process template", uids={"persistent_id": "uid_3"}, conditions=[self.ct]
        )
        with self.assertRaises(KeyError):
            p = Process("process", template=pt)

    def test_all_initializations(self):
        """testing initialization of all types of BaseElement object"""

        self.assertTrue(len(gemd_template_store.all_template_stores.keys()), 1)
        self.assertTrue("test" in gemd_template_store.all_template_stores.keys())
        # template_store.global_template_store

        ###### initializing by subclassing
        a = ArcMelting("arc melting")
        self.assertIn("auto", a.TEMPLATE.uids.keys())
        self.assertIn("persistent_id", a.TEMPLATE.uids.keys())
        self.assertEquals(len(a.TEMPLATE.parameters), 5)
        self.assertEquals(len(a._ATTRS["parameters"]), 5)
        self.assertEquals(len(a.run.parameters), 0)
        self.assertEquals(len(a.spec.parameters), 2)
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_file, False)
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_memory, False)
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_subclass, True)
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_store, False)
        del a

        ######
        name_to_reuse = "process template 1"

        # initializing by passing a template
        t = ProcessTemplate(name_to_reuse, uids={"gen": "uid_1"})
        p = Process("process", template=t)
        self.assertIn("auto", p.TEMPLATE.uids.keys())
        self.assertIn("persistent_id", p.TEMPLATE.uids.keys())
        self.assertEquals(t.uids["auto"], p.TEMPLATE.uids["auto"])
        self.assertEquals(t.uids["gen"], "uid_1")
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_file, False)
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_memory, True)
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_subclass, False)
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_store, False)

        # initializing by subclassing and passing a template
        def instantiate(template_name):
            return ArcMelting(
                "arc melting",
                template=ProcessTemplate(
                    template_name,
                ),
            )

        with self.assertWarns(ResourceWarning):
            a = instantiate(name_to_reuse)  # reusing same name_to_reuse
        self.assertEquals("uid_1", a.TEMPLATE.uids["gen"])
        self.assertEquals(
            t.uids["auto"], a.TEMPLATE.uids["auto"]
        )  # reusing the same template that should have been saved to store by now
        instantiate("process template 2")
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_file, False)
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_memory, False)
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_subclass, False)
        self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_store, True)
        del t
        del p
        del a

        ###### initializing by passing a template with attribute templates
        pt = ProcessTemplate(
            "process template 3", uids={"gen": "uid_3"}, conditions=[self.ct]
        )
        p = Process("process", template=pt)
        self.assertEquals(pt.uids["auto"], p.TEMPLATE.uids["auto"])
        self.assertEquals(
            self.ct.uids["auto"], p.TEMPLATE.conditions[0][0].uids["auto"]
        )
        self.assertEquals(len(p.TEMPLATE.conditions), 1)
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_file, False)
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_memory, True)
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_subclass, False)
        self.assertEqual(p.TEMPLATE_WRAPPER["test"].from_store, False)
        del pt
        del p

    def test_process_initializations(self):
        """initializing by passing a template with attribute templates + actual attributes"""
        # TODO: do the same with materials
        # TODO: test way more
        # a)
        p = Process(
            "process",
            template=ProcessTemplate(
                "process template 4",
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
                "process template 5",
                conditions=[self.ct],
            ),
            conditions=[
                Condition(
                    "location",
                    value=NominalCategorical("X-Ray Panel"),
                    template=self.ct,
                )
            ],
            which="run",
        )
        self.assertEquals(
            self.ct.uids["auto"], p.run.conditions[0].template.uids["auto"]
        )
        del p

        p = Process(
            "process",
            template=ProcessTemplate(
                "process template 6",
                conditions=[self.ct],
            ),
            conditions=[
                Condition(
                    "location",
                    value=NominalCategorical("X-Ray Panel"),
                    template=self.ct,
                )
            ],
            which="both",
        )

        self.assertEquals(
            self.ct.uids["auto"], p.spec.conditions[0].template.uids["auto"]
        )
        self.assertEquals(
            self.ct.uids["auto"], p.run.conditions[0].template.uids["auto"]
        )

        del p
