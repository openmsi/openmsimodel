from gemd.demo import cake
from gemd.json import GEMDJson
from gemd.entity.util import complete_material_history
from openmsimodel.subworkflow.process_block import ProcessBlock
from openmsimodel.entity.base import Material, Process, Ingredient, Measurement
from gemd import ProcessTemplate, MaterialTemplate, MeasurementTemplate
import json


def main():
    encoder = GEMDJson()
    # cake = cake.make_cake(seed=42)

    process = Process(
        name="process_test", template=ProcessTemplate("process_template_test")
    )
    process.model_dump()
    material = Material(
        name="material_test", template=MaterialTemplate("material_template_test")
    )
    material.model_dump()

    # dest = "individual_jsons"
    # dump = False


if __name__ == "__main__":
    main()
