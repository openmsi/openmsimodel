from pathlib import Path
from gemd import (
    MaterialTemplate,
    ProcessTemplate,
    MeasurementTemplate,
    ParameterTemplate,
    RealBounds,
)
from openmsimodel.workflow.workflow import Workflow
from openmsimodel.subworkflow.process_block import ProcessBlock
from openmsimodel.entity.gemd.material import Material
from openmsimodel.entity.gemd.process import Process
from openmsimodel.entity.gemd.measurement import Measurement
from openmsimodel.entity.gemd.ingredient import Ingredient
from openmsimodel.db.open_db import OpenDB


# from openmsimodel.graph.open_graph import OpenGraph


def main():
    workflow = Workflow()

    alloy_ingredient = Ingredient("Alloy Ingredient")
    polishing_process = Process("Polishing", template=ProcessTemplate("Heating"))
    polished_alloy = Material("Polished Alloy", template=MaterialTemplate("Alloy"))
    polishing_block = ProcessBlock(
        name=f"Polishing Alloy",
        workflow=workflow,
        material=polished_alloy,
        ingredients=[alloy_ingredient],
        process=polishing_process,
        measurements=[],
    )
    polishing_block.link_within()

    polished_alloy_ingredient = Ingredient("Polished Alloy Ingredient")
    heating_process = Process(
        "Heating",
        template=ProcessTemplate(
            "Heating",
            parameters=ParameterTemplate(
                name="Temperature",
                bounds=RealBounds(0, 1500, "Kelvin"),
            ),
        ),
    )
    heated_alloy = Material("Heated Alloy", template=MaterialTemplate("Alloy"))
    heating_block = ProcessBlock(
        name=f"Heating Alloy",
        workflow=workflow,
        material=heated_alloy,
        ingredients=[polished_alloy_ingredient],
        process=heating_process,
        measurements=[],
    )
    heating_block.link_within()
    heating_block.link_prior(
        polishing_block, ingredient_name_to_link="Polished Alloy Ingredient"
    )

    to_be_visualized = heating_block.gemd_assets
    output = str(Path().absolute() / "output")
    # open_graph = OpenGraph(
    #     name="heating", source=to_be_visualized, output=output, which="all"
    # )
    # G, relabeled_G, name_mapping = open_graph.build_graph()

    block = ProcessBlock.from_spec_or_run(
        str(polishing_process.name + "_backward"),
        notes=None,
        spec=polishing_process.spec,
        run=polishing_process.run,
    )
    r


if __name__ == "__main__":
    main()
