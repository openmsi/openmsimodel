import json, glob, os, csv, time
import random, pathlib

from openmsimodel.db.gemd_database import MSSQLDatabase
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from openmsimodel.utilities.runnable import Runnable
from openmsimodel.utilities.logging import Logger

# from openmsimodel.db.queries import load_model_query
import openmsimodel.db.queries as queries


from inspect import getmembers, isfunction

local = True
try:
    from IPython import get_ipython
    exec_env = get_ipython().__class__.__name__
    if exec_env == "ZMQInteractiveShell":  # ran locally
        local = False
except Exception as e:
    print(f"Import ERROR: {e}")
if local:
    from PyInquirer import prompt, Separator

from pprint import pprint


def create_acronym(phrase):
    acronym = ""
    words = phrase.split("_")
    for word in words:
        acronym += word[0].upper()
    return acronym


class OpenDB(Runnable):
    """Class to interact with model artefacts in a database, allowing long-term storage of assets, faster and richer data retrieval, etc.
    The module typically extract knowledges directly from JSONs of GEMD objects, and maps the GEMD Json structure to SQL classes (see prepare_classes in queries.py).
    JSONs remain the main method of communication across the packages, from model instantiatiation to graphers.
    """

    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, database_name, private_path, output):
        with open(private_path, "r") as f:
            self.auth = json.load(f)
        self.database = database_name  # GEMD
        self.gemd_db = MSSQLDatabase(self.auth, self.database)
        self.output = output
        self.listed_functions = {}
        self.listed_acronyms = {}
        for function_name, function in getmembers(queries, isfunction):
            acc = create_acronym(function_name)
            self.listed_acronyms[acc] = function_name
            self.listed_functions[function_name] = (function, acc)

        self.logger = Logger()

    def load_model(self, name, dirpath, uuid="auto"):
        return queries.load_model_query(name, self.gemd_db, dirpath, uuid)

    def create_tables(self):
        return queries.create_tables_query()

    def print_and_dump(self, sql_results, query, name, dump=True):
        """_summary_

        Args:
            sql_results (_type_): _description_
            query (_type_): _description_
            name (_type_): _description_
        """
        output_file = os.path.join(
            self.output,
            name
            + str(time.strftime("%_m%d%Y%H%M", time.localtime()))
            + "_"
            + str(random.randint(0, 10000))
            + ".csv",
        )
        print(sql_results)
        sql_results.to_csv(output_file)
        if not dump:
            with open(output_file, "a") as fp:
                w = csv.writer(fp)
                w.writerow("\n")
                w.writerow([query])
        return sql_results

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        args = [*superargs, "database_name", "private_path", "output"]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        open_db = cls(args.database_name, args.private_path, args.output)
        try:
            while True:
                select_mode_question = [
                    {
                        "type": "list",
                        "name": "mode",
                        "message": "Select interactive mode: ",
                        "choices": [
                            "load_model",
                            "listed_queries",
                            "custom_query",
                            "add_schema",
                        ],
                    }
                ]
                answer = prompt(select_mode_question)
                if not "mode" in answer.keys():
                    raise KeyError('Expected a value for key "mode", but not found.')
                mode = answer["mode"]
                if mode == "add_schema":
                    try:
                        add_schema_query = queries.create_tables_query()
                        result = open_db.gemd_db.execute_query(add_schema_query)
                        open_db.print_and_dump(
                            result, add_schema_query, "add_schema_query"
                        )
                    except Exception as e:
                        print(f"ERROR: {e}. ")
                        print("Try again.")
                    # pass
                elif mode == "load_model":
                    load_model_question = {
                        "type": "input",
                        "name": "load_model_params",
                        "message": "Enter the appropriate parameters for loading a model: ",
                    }
                    answer = prompt(load_model_question)
                    params = answer["load_model_params"].split(" ")
                    open_db.load_model(params[0], params[1])
                elif mode == "listed_queries":
                    # providing documentationon available queries
                    def list_queries():
                        for function_name, (
                            function,
                            function_accronym,
                        ) in open_db.listed_functions.items():
                            open_db.logger.info(
                                f"-  name: {function_name}, acronym: {function_accronym}, description: {function.__doc__} "
                            )

                    show_documentation_question = {
                        "type": "confirm",
                        "name": "display",
                        "message": "Would you like to display documentation on listed queries? (Enter to skip) ",
                        "default": False,
                    }
                    answer = prompt(show_documentation_question)
                    display = answer["display"]
                    if display:
                        list_queries()

                    # specifying query
                    select_query_question = {
                        "type": "input",
                        "name": "selected_query",
                        "message": "Enter query with its required arguments: ",
                    }
                    answer = prompt(select_query_question)
                    selected_query = answer["selected_query"].split(" ")
                    identifier = selected_query[0]
                    try:
                        if (
                            identifier in open_db.listed_acronyms.keys()
                            or identifier.upper() in open_db.listed_acronyms.keys()
                        ):  # passed the acronym
                            name = open_db.listed_acronyms[identifier.upper()]
                            func = open_db.listed_functions[name][0]
                        elif (
                            identifier in open_db.listed_functions.keys()
                            or identifier.lower() in open_db.listed_functions.keys()
                        ):  # passed whole name
                            func = open_db.listed_functions[identifier.lower()][0]
                        else:
                            raise KeyError(
                                f"couldn't recognize the identifier passed as '{identifier}'. Pass the full name or acronym. "
                            )
                        selected_query = func(*selected_query[1:])
                        result = open_db.gemd_db.execute_query(selected_query)
                        open_db.print_and_dump(result, selected_query, identifier)
                    except Exception as e:
                        print(f"ERROR: {e}")
                        print("Try again.")
                elif mode == "custom_query":  # custom query
                    enter_custom_query_question = {
                        "type": "input",
                        "name": "custom_query",
                        "message": "Enter a custom query:",
                        "default": "",
                    }
                    answer = prompt(enter_custom_query_question)
                    custom_query = answer["custom_query"]

                    open_db.logger.info("executing custom query...")
                    open_db.logger.info(f"query: {custom_query}")
                    try:
                        result = open_db.gemd_db.execute_query(custom_query)
                        open_db.print_and_dump(result, custom_query, "custom_query")
                    except Exception as e:
                        print(f"ERROR: {e}. ")
                        print("Try again.")
                    open_db.logger.info("Done.")
        except KeyboardInterrupt:
            pass


def main(args=None):
    """
    Main method to run from command line
    """
    OpenDB.run_from_command_line(args)


if __name__ == "__main__":
    main()
