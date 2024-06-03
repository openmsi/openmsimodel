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

def recursive_call(template, definition_ref, definitions):
    definition_name = definition_ref.split("/")[-1]
    print(f"- Adding {definition_name}...")
    process(template, definitions[definition_name], definitions)

def process(template, schema, definitions = {}):
    _dict = {}
    required_args = []
    validate = None
    if "properties" in schema:
        _dict = schema["properties"]
    elif "oneOf" in schema:
        if "allOf" in schema["oneOf"][0].keys(): # for attribute templates
            _dict = schema["oneOf"][0]["allOf"][0]["properties"]
            extra  = schema["oneOf"][0]["allOf"][1]['properties']
            for key, value in extra.items():
                _dict[key] = value  
            required_args = schema["oneOf"][0]["allOf"][0]["required"]
        else:
            _dict = schema["oneOf"][0]["properties"] # object templates
            required_args = schema["oneOf"][0]["required"]
        if "definitions" in schema.keys():
            definitions = {**definitions, **schema["definitions"]}
    # print(f"- Adding {_dict['type']['const']}...")
    for key, value in _dict.items():
        field_name = key
        field_type = value.get("type")
        field_description = value.get("description", "")
        if "const" in value.keys(): 
            template[field_name] = value["const"]
            continue
        if "$ref" in value.keys(): # applies to tags
            recursive_call(template, value["$ref"], definitions)
        if "items" in value.keys() and "items" in value["items"].keys(): # applies to attributes schema structure 
            for i, item in enumerate((value["items"]["items"])):
                if "$ref" in item:
                    recursive_call(template, item["$ref"], definitions)
        if field_type == "array":
            if field_name in required_args:
                validate = lambda text: text != "" or "The field is required.."
            response = questionary.text(
                f"{field_name} ({field_description}). Please, Enter space-separated list of values: ",
                validate = validate
            ).ask()
            values = response.split(" ")
            values = [value.strip() for value in values]
            template[field_name] = values
        elif field_type == "string":
            if field_name in required_args:
                validate = lambda text: text != "" or "The field is required. "
            template[field_name] = questionary.text(
                f"{field_name} ({field_description})",
                validate = validate
                ).ask()
        elif field_type == "number":
            template[field_name] = questionary.text(f"{field_name} ({field_description})", 
                validate=lambda text: text.isdigit() or "Please enter a valid number.").ask()
        validate = None
        
    print("Done.")


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
