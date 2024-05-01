import questionary
from questionary import prompt, select, text, confirm
from inspect import getmembers, isfunction
from jsonschema import validate
from gemd_schema.object_templates import (
    process_template,
    material_template,
    measurement_template,
)
from gemd_schema.run import process_run, ingredient_run, measurement_run, material_run

object_template_schemas = [process_template, material_template, measurement_template]


def process(template, schema):
    _dict = {}
    required_args = []
    if "properties" in schema:
        _dict = schema["properties"]
    elif "oneOf" in schema:
        _dict = schema["oneOf"][0]["properties"]
        required_args = schema["oneOf"][0]["required"]
        definitions = schema["definitions"]
    for key, value in _dict.items():
        field_name = key
        field_type = value.get("type")
        field_description = value.get("description", "")
        if "const" in value.keys():
            template[field_name] = value["const"]
            continue
        if "$ref" in value.keys():
            definition_name = value["$ref"].split("/")[-1]
            process(template, definitions[definition_name])

        if field_type == "array":
            response = questionary.text(
                f"{field_name} ({field_description}) \nEnter comma-separated list of values"
            ).ask()
            values = response.split(",")
            values = [value.strip() for value in values]
            template[field_name] = values
        elif field_type == "string":
            template[field_name] = questionary.text(field_description).ask()
        if field_name in required_args and template[field_name] is None:
            raise ValueError(f"{field_name} is required.")


def process_all():
    template = {}
    for object_template_schema in object_template_schemas:
        process(template, object_template_schema)

        # Validate the input based on the schema
        validate(instance=template, schema=object_template_schema)

        # Use the populated template object
        print(template)


def main():
    process_all()


if __name__ == "__main__":
    main()
