===============
Overview
===============

.. .. notebook:: ../../../examples/materials_data/materials_data.ipynb
..    :cell-count: 10
..    :class: output

Complete installation steps and add the following imports:

.. code-block:: bash

    from gemd import MaterialTemplate, ProcessTemplate, MeasurementTemplate

.. code-block:: bash

    from openmsimodel.science_kit.science_kit import ScienceKit
    from openmsimodel.tools.structures.materials_sequence import MaterialsSequence
    from openmsimodel.entity.gemd.material import Material
    from openmsimodel.entity.gemd.process import Process
    from openmsimodel.entity.gemd.measurement import Measurement
    from openmsimodel.db.open_db import OpenDB
    from openmsimodel.graph.open_graph import OpenGraph

.. code-block:: bash

    from pathlib import Path 

Then, start interacting with OpenMSIModel by:

* Building a GEMD Object and wrap it with a Element class:

.. code-block:: bash

    process = Process("Heating", template=ProcessTemplate("Heating"))
    material = Material("Heated Alloy", template=MaterialTemplate("Heated Alloy"))

* Organize them as desired, and encapsulates all your knowledge and tools in your science kit:

.. code-block:: bash
   
   w = ScienceKit()
   block = MaterialsSequence(
        name=f"Heating Block",
        science_kit=w,
        material=material,
        ingredients={},
        process=process,
        measurements={},
   )
   block.link_within() # 4 links completed in one statement

* Visualize your objects with OpenGraph:

.. code-block:: bash

    to_be_visualized = block.return_all_gemd()
    output = str(Path().absolute() / "output")
    print(output)
    assets_to_add = {
            "add_attributes": 1,
            "add_file_links": 1,
            "add_tags": 1,
        }
    open_graph = OpenGraph("Heating Block", dirpath=to_be_visualized, output=output, layout='visualization', add_bidirectional_edges=False)
    G, relabeled_G, name_mapping = open_graph.build_graph(
        assets_to_add=assets_to_add,
        add_separate_node=False,
        which='all',
    )

* Query them with OpenDB:

.. code-block:: bash

    db_name = "GEMD"
    open_db = OpenDB(database_name=db_name, private_path="/path/to/private/key", output=output)

    table_name = "heating_block_table"
    open_db.load_model(table_name, dirpath=output)
    open_db.custom_query("select top 3 context from gemdobject c where c.model_id={}".format(table_name))