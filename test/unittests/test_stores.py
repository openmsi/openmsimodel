# imports
import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")

from data.subclassing.arcmelting_example_subclass import ArcMeltingExample
from openmsimodel.entity.impl import assign_uuid

from openmsimodel.stores.gemd_template_store import GEMDTemplateStore
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


class TestStores(unittest.TestCase):
    # TODO: test define attributes when the same attribute is repassed

    def test_stores(self):
        """testing stores"""

        #######
        # run_all_tests will run test_entity_base_instantiation first, which populates the stores already wit ArcMeltingExample initiations for example,
        # in which case both declarations below should return a warning for template already in file but still have the same template by uid
        # Expected: should get warnings with existing

        with self.assertWarns(ResourceWarning):
            a = ArcMeltingExample("arc melting")
            first_auto_uid = ArcMeltingExample.TEMPLATE.uids["auto"]
            a = ArcMeltingExample("arc melting")
            self.assertEquals(first_auto_uid, a.TEMPLATE.uids["auto"])
        # self.assertNotEquals(first_auto_uid, a.TEMPLATE.uids["auto"])

        ######
        dummy_root = Path(__file__).parent.parent / "data/stores/dummy_store"
        dummy_template_store = GEMDTemplateStore(load_all_files=False)

        # testing property setter
        dummy_template_store.root = dummy_root
        self.assertEquals(
            dummy_template_store.root,
            Path(__file__).parent.parent / "data/stores/dummy_store",
        )

        # testing initializing store
        dummy_template_store.initialize_store()

        for root, dirs, files in os.walk(dummy_root):
            self.assertTrue(len(files) == 1)
            self.assertEqual(
                os.path.join(root, files[0]), str(dummy_template_store.registry_path)
            )
            for dir in dirs:
                full_dir = Path(os.path.join(root, dir))
                self.assertTrue(full_dir in dummy_template_store.store_folders.values())
            break

        # testing register_template
        name = "dummy template 1"
        template = ProcessTemplate(name)
        _type = type(template)
        destination = dummy_template_store.store_folders[_type]

        with self.assertRaises(TypeError):
            dummy_template_store.register_new_template("str", from_file=False)

        # with self.assertRaises(RuntimeError):  # doesn't have uid so must be set
        #     dummy_template_store.register_new_template(template, from_file=False)
        # assign_uuid(template, "auto")
        self.assertEqual(len(os.listdir(destination)), 0)
        dummy_template_store.register_new_template(template, from_file=False)
        self.assertEqual(len(os.listdir(destination)), 1)
        self.assertEqual(len(dummy_template_store._object_templates[_type]), 1)
        self.assertEqual(
            dummy_template_store._object_templates[_type][name].template.name,
            name,
        )
        self.assertTrue(
            "auto"
            in dummy_template_store._object_templates[_type][name].template.uids.keys()
        )

        with self.assertWarns(ResourceWarning):
            dummy_template_store.register_new_template(template, from_file=False)
        self.assertEqual(
            len(dummy_template_store._object_templates[_type]), 1
        )  # make sure it hasn't been added, as the already registered template should have been used

        # with self.assertWarns(ResourceWarning): #TODO: this raises a keyerror so THINK ABOUT This scenario. GOOD but think about encoder inside the store, etcs
        #     p = Process("dummy Process", template=template)

        # dummy_template_store.register_all_templates_from_files()
