# imports
import pkg_resources, subprocess, unittest, sys, importlib
from pathlib import Path
import os

sys.path.insert(0, "..")

from data.subclassing.arcmelting import ArcMelting
from openmsimodel.entity.gemd.impl import assign_uuid

from openmsimodel.stores.gemd_template_store import GEMDTemplateStore, stores_config

from openmsimodel.entity.gemd.gemd_element import GEMDElement
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.entity.gemd.measurement import Measurement


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

    # testing type of initialization 1 (see 1b for type of initialization 2)

    dummy_root = Path(__file__).parent.parent / "data/stores/dummy_store"
    # dummy_template_store = GEMDTemplateStore(id="dummy", load_all_files=False)

    stores_config.designated_store_id = "dummy"
    stores_config.deploy_store("dummy")
    # stores_config.all_template_stores["test"].root = dummy_root
    # stores_config.all_template_stores["test"].register_all_templates_from_store()

    # self.assertEqual(len(template_store_ids), 3)
    # self.assertTrue("dummy" in template_store_ids)

    def test_stores(self):
        """testing stores"""

        #######
        # run_all_tests will run test_entity_base_instantiation first, which populates the stores already wit ArcMelting initiations for example,
        # in which case both declarations below should return a warning for template already in file but still have the same template by uid
        # Expected: should get warnings with existing

        # with self.assertWarns(ResourceWarning):
        a = ArcMelting("arc melting")
        first_auto_uid = ArcMelting.TEMPLATE.uids["auto"]
        a_2 = ArcMelting("arc melting")
        self.assertEquals(first_auto_uid, a_2.TEMPLATE.uids["auto"])
        # if (
        #     global_template_store.id == "global"
        # ):  # if ran on its own TODO: review bc global template reads from gloabl stores
        # if (
        #     len(stores_config.all_template_stores.keys()) == 1
        #     and "global" in stores_config.all_template_stores.keys()
        # ):
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_file, False)
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_memory, False)
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_subclass, True)
        #     self.assertEqual(a.TEMPLATE_WRAPPER["global"].from_store, False)
        if (
            "test" in stores_config.all_template_stores.keys()
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
        stores_config.all_template_stores["dummy"].root = self.dummy_root
        self.assertEquals(
            stores_config.all_template_stores["dummy"].root,
            Path(__file__).parent.parent / "data/stores/dummy_store",
        )

        ##### testing initializing store
        stores_config.all_template_stores["dummy"].initialize_store()

        for root, dirs, files in os.walk(self.dummy_root):
            self.assertTrue(len(files) == 1)
            self.assertEqual(
                os.path.join(root, files[0]),
                str(stores_config.all_template_stores["dummy"].registry_path),
            )
            for dir in dirs:
                full_dir = Path(os.path.join(root, dir))
                self.assertTrue(
                    full_dir
                    in stores_config.all_template_stores["dummy"].store_folders.values()
                )
            break

        ###### testing register_template on a process template
        template = ProcessTemplate("dummy process template 1")
        _type = type(template)
        process_templates_destination = stores_config.all_template_stores[
            "dummy"
        ].store_folders[_type]

        with self.assertRaises(TypeError):
            stores_config.all_template_stores["dummy"].register_new_template(
                "str", from_store=False
            )

        self.assertEqual(len(os.listdir(process_templates_destination)), 0)
        stores_config.all_template_stores["dummy"].register_new_template(
            template, from_store=False
        )
        self.assertEqual(len(os.listdir(process_templates_destination)), 1)
        self.assertEqual(
            len(stores_config.all_template_stores["dummy"]._object_templates[_type]), 1
        )
        self.assertEqual(
            stores_config.all_template_stores["dummy"]
            ._object_templates[_type]["dummy process template 1"]
            .template.name,
            "dummy process template 1",
        )
        self.assertTrue(
            "auto"
            in stores_config.all_template_stores["dummy"]
            ._object_templates[_type]["dummy process template 1"]
            .template.uids.keys()
        )

        with self.assertWarns(
            ResourceWarning
        ):  # make sure it hasn't been added, as the already registered template should have been used
            stores_config.all_template_stores["dummy"].register_new_template(
                template, from_store=False
            )
        self.assertEqual(
            len(stores_config.all_template_stores["dummy"]._object_templates[_type]), 1
        )

        ###### testing register_template on a process template + attribute template (each individually)
        pt = ParameterTemplate(
            "dummy parameter template 1", bounds=RealBounds(0, 48, "hr")
        )
        template = ProcessTemplate("dummy process template 2", parameters=[pt])
        _type = type(pt)
        parameter_templates_destination = stores_config.all_template_stores[
            "dummy"
        ].store_folders[_type]

        self.assertEqual(len(os.listdir(parameter_templates_destination)), 0)

        stores_config.all_template_stores["dummy"].register_new_template(
            template, from_store=False
        )  # template
        stores_config.all_template_stores["dummy"].register_new_template(
            pt, from_store=False
        )  # attr

        self.assertEqual(len(os.listdir(parameter_templates_destination)), 1)  # + 1
        self.assertEqual(
            len(stores_config.all_template_stores["dummy"]._attribute_templates[_type]),
            1,
        )

        self.assertEqual(len(os.listdir(process_templates_destination)), 2)  # + 1
        self.assertEqual(
            len(
                stores_config.all_template_stores["dummy"]._object_templates[
                    type(template)
                ]
            ),
            2,
        )

    def test_dummy_store_with_Element(self):
        # test store is manipulated in test_entity_base_instantiation prior (expected and useful for testing across files)
        test_processes_count = len(
            stores_config.all_template_stores["test"]._object_templates[ProcessTemplate]
        )
        test_params_count = len(
            stores_config.all_template_stores["test"]._attribute_templates[
                ParameterTemplate
            ]
        )
        self.assertEqual(test_processes_count, 8)
        self.assertEqual(test_params_count, 5)

        # adding dummy store
        self.assertEqual(len(stores_config.all_template_stores), 1)
        stores_config.all_template_stores["dummy"] = stores_config.all_template_stores[
            "dummy"
        ]
        self.assertEqual(len(stores_config.all_template_stores), 2)

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
            test_processes = stores_config.all_template_stores[
                "test"
            ]._object_templates[ProcessTemplate]
            test_processes_destination = stores_config.all_template_stores[
                "test"
            ].store_folders[ProcessTemplate]
            helper_1(  # due to 1a), gets one more
                len(test_processes) - test_processes_count,
                1,
                len(os.listdir(test_processes_destination)) - test_processes_count,
                1,
            )
            test_parameters = stores_config.all_template_stores[
                "test"
            ]._attribute_templates[ParameterTemplate]
            test_parameters_destination = stores_config.all_template_stores[
                "test"
            ].store_folders[ParameterTemplate]

            helper_1(  # due to 1a), gets one more
                (len(test_parameters) - test_params_count),
                1,
                len(os.listdir(test_parameters_destination)) - test_params_count,
                1,
            )

            # dummy asserts
            dummy_processes = stores_config.all_template_stores[
                "dummy"
            ]._object_templates[ProcessTemplate]
            dummy_processes_destination = stores_config.all_template_stores[
                "dummy"
            ].store_folders[ProcessTemplate]
            helper_1(  # due to 1a), gets one more
                len(dummy_processes),
                3,
                len(os.listdir(dummy_processes_destination)),
                3,
            )
            dummy_parameters = stores_config.all_template_stores[
                "dummy"
            ]._attribute_templates[ParameterTemplate]
            dummy_parameters_destination = stores_config.all_template_stores[
                "dummy"
            ].store_folders[ParameterTemplate]
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

        test_processes = stores_config.all_template_stores["test"]._object_templates[
            ProcessTemplate
        ]
        processes_destination = stores_config.all_template_stores["test"].store_folders[
            ProcessTemplate
        ]
        # no addition at all for both tests and dummy
        #  why? template already exists and is reused with the attributes that come with it!
        # 1a) and 1b) have the same exepcted results
        reusable_tests()

        ##### 1) c) same as above with already existing attr template in store
        p = Process(
            "dummy process 1",
            template=ProcessTemplate(
                "dummy process template 4",  # new process
                parameters=[
                    ParameterTemplate(
                        "dummy parameter template 2",  # already existing param
                        bounds=RealBounds(0, 10, "m"),
                    )
                ],
            ),
        )

        test_processes = stores_config.all_template_stores["test"]._object_templates[
            ProcessTemplate
        ]
        processes_destination = stores_config.all_template_stores["test"].store_folders[
            ProcessTemplate
        ]
        # this time 1c) has diff exepected results
        # both dictionary gets one more process template... but same parameter templates!
        helper_1(
            len(test_processes) - test_processes_count,
            1 + 1,
            len(os.listdir(processes_destination)) - test_processes_count,
            1 + 1,
        )
        test_parameters = stores_config.all_template_stores[
            "test"
        ]._attribute_templates[ParameterTemplate]
        parameters_destination = stores_config.all_template_stores[
            "test"
        ].store_folders[ParameterTemplate]
        helper_1(
            (len(test_parameters) - test_params_count),
            1,
            len(os.listdir(parameters_destination)) - test_params_count,
            1,
        )

        dummy_processes = stores_config.all_template_stores["dummy"]._object_templates[
            ProcessTemplate
        ]
        dummy_processes_destination = stores_config.all_template_stores[
            "dummy"
        ].store_folders[ProcessTemplate]
        helper_1(
            len(dummy_processes),
            4,
            len(os.listdir(dummy_processes_destination)),
            4,
        )
        dummy_parameters = stores_config.all_template_stores[
            "dummy"
        ]._attribute_templates[ParameterTemplate]
        dummy_parameters_destination = stores_config.all_template_stores[
            "dummy"
        ].store_folders[ParameterTemplate]
        helper_1(
            len(dummy_parameters),
            2,
            len(os.listdir(dummy_parameters_destination)),
            2,
        )

    # def test_multi_stores(self):
    # TODO: do tests with 2 diff orders, check which one gets pulled from

    # TODO: test stores_config.all_template_stores["dummy"].register_all_templates_from_files()

    # TODO: tests the n's, the from_ mroe extensively,
