# imports
import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")

from data.subclassing.arcmelting_example_subclass import ArcMeltingExample
from openmsimodel.entity.impl import assign_uuid

# import openmsimodel.stores.gemd_template_store as template_store
# from template_store import GEMDTemplateStore, global_template_store
from openmsimodel.stores.gemd_template_store import (
    GEMDTemplateStore,
    all_template_stores,
    template_store_ids,
)

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
    RealBounds,
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

    # def test_global_store_ids_list(self):
    # self.assertEqual(len(template_store_ids), 2)
    # self.assertTrue("global" in template_store_ids)
    # self.assertTrue("test" in template_store_ids)

    dummy_root = Path(__file__).parent.parent / "data/stores/dummy_store"
    dummy_template_store = GEMDTemplateStore(id="dummy", load_all_files=False)
    # self.assertEqual(len(template_store_ids), 3)
    # self.assertTrue("dummy" in template_store_ids)

    def test_stores(self):
        """testing stores"""

        #######
        # run_all_tests will run test_entity_base_instantiation first, which populates the stores already wit ArcMeltingExample initiations for example,
        # in which case both declarations below should return a warning for template already in file but still have the same template by uid
        # Expected: should get warnings with existing

        with self.assertWarns(ResourceWarning):
            a = ArcMeltingExample("arc melting")
            first_auto_uid = ArcMeltingExample.TEMPLATE.uids["auto"]
            a_2 = ArcMeltingExample("arc melting")
            self.assertEquals(first_auto_uid, a_2.TEMPLATE.uids["auto"])
        # if (
        #     global_template_store.id == "global"
        # ):  # if ran on its own TODO: review bc global template reads from gloabl stores
        # if (
        #     len(all_template_stores.keys()) == 1
        #     and "global" in all_template_stores.keys()
        # ):
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_file, False)
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_memory, False)
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_subclass, True)
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_store, False)
        if (
            "test" in all_template_stores.keys()
        ):  # when all tests are ran. in this case, other tests are ran prior to this one and affect the store
            self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_file, False)
            self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_memory, False)
            self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_subclass, False)
            self.assertEqual(a.TEMPLATE_WRAPPER["test"].from_store, True)
            self.assertEqual(a_2.TEMPLATE_WRAPPER["test"].from_file, False)
            self.assertEqual(a_2.TEMPLATE_WRAPPER["test"].from_memory, False)
            self.assertEqual(a_2.TEMPLATE_WRAPPER["test"].from_subclass, False)
            self.assertEqual(a_2.TEMPLATE_WRAPPER["test"].from_store, True)
        del a
        del a_2
        # self.assertNotEquals(first_auto_uid, a.TEMPLATE.uids["auto"])

    def test_dummy_store(self):
        ###### testing property setter
        self.dummy_template_store.root = self.dummy_root
        self.assertEquals(
            self.dummy_template_store.root,
            Path(__file__).parent.parent / "data/stores/dummy_store",
        )

        ##### testing initializing store
        self.dummy_template_store.initialize_store()

        for root, dirs, files in os.walk(self.dummy_root):
            self.assertTrue(len(files) == 1)
            self.assertEqual(
                os.path.join(root, files[0]),
                str(self.dummy_template_store.registry_path),
            )
            for dir in dirs:
                full_dir = Path(os.path.join(root, dir))
                self.assertTrue(
                    full_dir in self.dummy_template_store.store_folders.values()
                )
            break

        ###### testing register_template on a process template
        template = ProcessTemplate("dummy process template 1")
        _type = type(template)
        process_templates_destination = self.dummy_template_store.store_folders[_type]

        with self.assertRaises(TypeError):
            self.dummy_template_store.register_new_template("str", from_store=False)

        self.assertEqual(len(os.listdir(process_templates_destination)), 0)
        self.dummy_template_store.register_new_template(template, from_store=False)
        self.assertEqual(len(os.listdir(process_templates_destination)), 1)
        self.assertEqual(len(self.dummy_template_store._object_templates[_type]), 1)
        self.assertEqual(
            self.dummy_template_store._object_templates[_type][
                "dummy process template 1"
            ].template.name,
            "dummy process template 1",
        )
        self.assertTrue(
            "auto"
            in self.dummy_template_store._object_templates[_type][
                "dummy process template 1"
            ].template.uids.keys()
        )

        with self.assertWarns(
            ResourceWarning
        ):  # make sure it hasn't been added, as the already registered template should have been used
            self.dummy_template_store.register_new_template(template, from_store=False)
        self.assertEqual(len(self.dummy_template_store._object_templates[_type]), 1)

        ###### testing register_template on a process template + attribute template (each individually)
        pt = ParameterTemplate(
            "dummy parameter template 1", bounds=RealBounds(0, 48, "hr")
        )
        template = ProcessTemplate("dummy process template 2", parameters=[pt])
        _type = type(pt)
        parameter_templates_destination = self.dummy_template_store.store_folders[_type]

        self.assertEqual(len(os.listdir(parameter_templates_destination)), 0)

        self.dummy_template_store.register_new_template(
            template, from_store=False
        )  # template
        self.dummy_template_store.register_new_template(pt, from_store=False)  # attr

        self.assertEqual(len(os.listdir(parameter_templates_destination)), 1)  # + 1
        self.assertEqual(len(self.dummy_template_store._attribute_templates[_type]), 1)

        self.assertEqual(len(os.listdir(process_templates_destination)), 2)  # + 1
        self.assertEqual(
            len(self.dummy_template_store._object_templates[type(template)]), 2
        )

    def test_dummy_store_with_basenode(self):
        # test store is manipulated in test_entity_base_instantiation prior (expected and useful for testing across files)
        test_processes_count = len(
            all_template_stores["test"]._object_templates[ProcessTemplate]
        )
        test_params_count = len(
            all_template_stores["test"]._attribute_templates[ParameterTemplate]
        )
        self.assertEqual(test_processes_count, 8)
        self.assertEqual(test_params_count, 5)

        # adding dummy store
        self.assertEqual(len(all_template_stores), 1)
        all_template_stores["dummy"] = self.dummy_template_store
        self.assertEqual(len(all_template_stores), 2)

        ##### 1) a) instantiation of base node object, which should register an object template and attribute template
        p = Process(
            "dummy process 1",
            template=ProcessTemplate(
                "dummy process template 3",
                parameters=[
                    ParameterTemplate(
                        "dummy parameter template 2", bounds=RealBounds(0, 10, "m")
                    )
                ],
            ),
        )

        ######
        def helper_1(one, two, three, four):
            self.assertEqual(one, two)
            self.assertEqual(three, four)

        def reusable_tests():
            # test asserts
            test_processes = all_template_stores["test"]._object_templates[
                ProcessTemplate
            ]
            test_processes_destination = all_template_stores["test"].store_folders[
                ProcessTemplate
            ]
            helper_1(  # due to 1a), gets one more
                len(test_processes) - test_processes_count,
                1,
                len(os.listdir(test_processes_destination)) - test_processes_count,
                1,
            )
            test_parameters = all_template_stores["test"]._attribute_templates[
                ParameterTemplate
            ]
            test_parameters_destination = all_template_stores["test"].store_folders[
                ParameterTemplate
            ]

            helper_1(  # due to 1a), gets one more
                (len(test_parameters) - test_params_count),
                1,
                len(os.listdir(test_parameters_destination)) - test_params_count,
                1,
            )

            # dummy asserts
            dummy_processes = all_template_stores["dummy"]._object_templates[
                ProcessTemplate
            ]
            dummy_processes_destination = all_template_stores["dummy"].store_folders[
                ProcessTemplate
            ]
            helper_1(  # due to 1a), gets one more
                len(dummy_processes),
                3,
                len(os.listdir(dummy_processes_destination)),
                3,
            )
            dummy_parameters = all_template_stores["dummy"]._attribute_templates[
                ParameterTemplate
            ]
            dummy_parameters_destination = all_template_stores["dummy"].store_folders[
                ParameterTemplate
            ]
            helper_1(  # due to 1a),  gets one more too!
                len(dummy_parameters),
                2,
                len(os.listdir(dummy_parameters_destination)),
                2,
            )

        reusable_tests()

        ##### 1) b) same as above with already existing object template in store
        with self.assertWarns(ResourceWarning):
            p = Process(
                "dummy process 1",
                template=ProcessTemplate(
                    "dummy process template 3",  # same process
                    parameters=[
                        ParameterTemplate(
                            "dummy parameter template 4",
                            bounds=RealBounds(0, 10, "m"),  # new param
                        )
                    ],
                ),
            )

        test_processes = all_template_stores["test"]._object_templates[ProcessTemplate]
        processes_destination = all_template_stores["test"].store_folders[
            ProcessTemplate
        ]
        # no addition at all for both tests and dummy
        #  why? template already exists and is reused with the attributes that come with it!
        # 1a) and 1b) have the same exepcted results
        reusable_tests()
        # helper_1(
        #     len(test_processes) - test_processes_count,
        #     1,
        #     len(os.listdir(processes_destination)) - test_processes_count,
        #     1,
        # )
        # test_parameters = all_template_stores["test"]._attribute_templates[
        #     ParameterTemplate
        # ]
        # parameters_destination = all_template_stores["test"].store_folders[
        #     ParameterTemplate
        # ]
        # helper_1(
        #     (len(test_parameters) - test_params_count),
        #     1,
        #     len(os.listdir(parameters_destination)) - test_params_count,
        #     1,
        # )

        # dummy_processes = all_template_stores["dummy"]._object_templates[
        #     ProcessTemplate
        # ]
        # dummy_processes_destination = all_template_stores["dummy"].store_folders[
        #     ProcessTemplate
        # ]
        # helper_1(
        #     len(dummy_processes),
        #     3,
        #     len(os.listdir(dummy_processes_destination)),
        #     3,
        # )
        # dummy_parameters = all_template_stores["dummy"]._attribute_templates[
        #     ParameterTemplate
        # ]
        # dummy_parameters_destination = all_template_stores["dummy"].store_folders[
        #     ParameterTemplate
        # ]
        # helper_1(
        #     len(dummy_parameters),
        #     2,
        #     len(os.listdir(dummy_parameters_destination)),
        #     2,
        # )

        ##### 1) c) same as above with already existing attr template in store
        p = Process(
            "dummy process 1",
            template=ProcessTemplate(
                "dummy process template 4",  # new process
                parameters=[
                    ParameterTemplate(
                        "dummy parameter template 3",  # already existing param
                        bounds=RealBounds(0, 10, "m"),
                    )
                ],
            ),
        )

        test_processes = all_template_stores["test"]._object_templates[ProcessTemplate]
        processes_destination = all_template_stores["test"].store_folders[
            ProcessTemplate
        ]
        # gets one more process template!
        helper_1(
            len(test_processes) - test_processes_count,
            2,
            len(os.listdir(processes_destination)) - test_processes_count,
            2,
        )
        test_parameters = all_template_stores["test"]._attribute_templates[
            ParameterTemplate
        ]
        parameters_destination = all_template_stores["test"].store_folders[
            ParameterTemplate
        ]
        helper_1(
            (len(test_parameters) - test_params_count),
            1,
            len(os.listdir(parameters_destination)) - test_params_count,
            1,
        )

    # def test_multi_stores(self):

    # test with 2 diff orders

    # with self.assertWarns(ResourceWarning): #TODO: this raises a keyerror so THINK ABOUT This scenario. GOOD but think about encoder inside the store, etcs
    #     p = Process("dummy Process", template=template)

    # self.dummy_template_store.register_all_templates_from_files()