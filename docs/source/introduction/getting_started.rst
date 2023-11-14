===============
Getting Started
===============

To start working with OpenMSIModel, follow these steps to install and set up the library.

Installation
------------

You can install OpenMSIModel using pip:

.. code-block:: bash

   pip install gemd
   pip install openmsimodel

Build a GEMD Object and wrap it with a Element class:

.. code-block:: bash

    from pathlib import Path 
    from gemd import MaterialTemplate, ProcessTemplate, MeasurementTemplate
    from openmsimodel.science_kit.science_kit import ScienceKit
    from openmsimodel.tools.structures.materials_sequence import MaterialsSequence
    from openmsimodel.entity.gemd.material import Material
    from openmsimodel.entity.gemd.process import Process
    from openmsimodel.entity.gemd.measurement import Measurement
    from openmsimodel.db.open_db import OpenDB
    from openmsimodel.graph.open_graph import OpenGraph

.. code-block:: bash

    w = ScienceKit()
    process = Process("Heating", template=ProcessTemplate("Heating"))
    material = Material("Heated Alloy", template=MaterialTemplate("Heated Alloy"))
    block = MaterialsSequence(
        name=f"Heating Block",
        science_kit=w,
        material=material,
        ingredients={},
        process=process,
        measurements={},
    )
    block.link_within() # 4 links completed in one statement

Visualize your objects with OpenGraph:

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

Query them with OpenDB:

.. code-block:: bash

    db_name = "GEMD"
    open_db = OpenDB(database_name=db_name, private_path="/path/to/private/key", output=output)

    table_name = "heating_block_table"
    open_db.load_model(table_name, dirpath=output)
    open_db.custom_query("select top 3 context from gemdobject c where c.model_id={}".format(table_name))

Once installed, you'll be ready to use OpenMSIModel in your projects.

Usage
-----

OpenMSIModel provides several modules and classes for different aspects of materials data management. To begin using the library, you can explore the following modules:

- `ScienceKit.py`: Contains knowledge about materials science workflows. It encapsulates the process of building GEMD models and offers reading and dumping functionalities.

- `Tool.py`: Represents Subworkflows, flexible structures for structuring, discovering, and serializing GEMD model elements. Subworkflows can be used for various purposes, such as organizing data or facilitating analysis.

- `MaterialsSequence.py`: A type of Tool that coalesces GEMD elements into natural structures, including materials, ingredients, processes, and new materials. ProcessBlocks simplify data retrieval and model building.

- `Element.py`: Serves as an interface and wrapper for data modeling formats like GEMD. It abstracts the use of GEMD and encapsulates functionalities for controlling templates, specifications, and runs.

- `OpenGraph.py`: Provides modules to build and visualize networkx or graphviz objects from GEMD objects. It helps establish relationships between GEMD objects and produces various output formats.

- `OpenDB.py`: Allows interaction with a database for managing model artifacts. It provides capabilities for loading models, executing queries, and more.

With these modules, you can efficiently work with materials data, build models, and interact with databases. Check out the documentation for each module to learn more about their usage.
