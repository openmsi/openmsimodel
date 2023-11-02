import json
import random
import time
import os
from pathlib import Path

from questionary import prompt, select, text, confirm

from openmsimodel.db.gemd_database import MSSQLDatabase
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from openmsimodel.utilities.runnable import Runnable
from openmsimodel.utilities.logging import Logger
import openmsimodel.db.queries as queries

from inspect import getmembers, isfunction


def create_acronym(phrase):
    # Function to create an acronym from a phrase
    acronym = "".join(word[0].upper() for word in phrase.split("_"))
    return acronym


class OpenDB(Runnable):
    """Class to interact with model artefacts in a database, allowing long-term storage of assets, faster and richer data retrieval, etc.
    The module typically extract knowledges directly from JSONs of GEMD objects, and maps the GEMD Json structure to SQL classes (see prepare_classes in queries.py).
    JSONs remain the main method of communication across the packages, from model instantiatiation to graphers.
    """

    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, database_name, private_path, output):
        self.auth = None
        self.gemd_db = None
        self.output = output
        self.listed_functions = {}
        self.listed_acronyms = {}
        self.logger = Logger()

        self.setup(database_name, private_path)

    def setup(self, database_name, private_path):
        """
        Set up the OpenDB tool.

        :param database_name: Name of the database to connect to.
        :param private_path: Path to a JSON file containing database credentials.
        """
        try:
            with open(private_path, "r") as f:
                self.auth = json.load(f)
            self.database = database_name  # GEMD
            self.gemd_db = MSSQLDatabase(self.auth, self.database)
        except FileNotFoundError as e:
            self.logger.error(f"Error loading credentials: {e}")
            self.logger.warning("Database functionality disabled.")

    def list_queries(self):
        """
        List and display available queries along with their documentation.
        """
        for function_name, (
            function,
            function_acronym,
        ) in self.listed_functions.items():
            function_doc = function.__doc__ or "No documentation available"
            function_doc = function_doc.strip()

            max_doc_length = 240
            if len(function_doc) > max_doc_length:
                function_doc = function_doc[:max_doc_length] + " ..."

            print(f"- Name: {function_name}")
            print(f"  Acronym: {function_acronym}")
            print(f"  Description: {function_doc}")

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
        print(query)
        output_file = os.path.join(
            self.output,
            name
            + "_"
            + str(time.strftime("%m%d%Y_%H%M_", time.localtime()))
            + str(random.randint(0, 10000))
            + ".csv",
        )
        print(sql_results)
        sql_results.to_csv(output_file)
        if not dump:
            with open(output_file, "a") as fp:
                w = csv.writer(fp)
        return sql_results

    def list_queries(self):
        for function_name, (
            function,
            function_acronym,
        ) in self.listed_functions.items():
            function_doc = function.__doc__ or "No documentation available"
            function_doc = function_doc.strip()  # Remove leading/trailing whitespace

            # Truncate long docstrings for better readability
            max_doc_length = 240  # Adjust this value as needed
            if len(function_doc) > max_doc_length:
                function_doc = function_doc[:max_doc_length] + "..."

            print(f"- Name: {function_name}")
            print(f"  Acronym: {function_acronym}")
            print(f"  Description: {function_doc}")

    def interactive_mode(self):
        try:
            while True:
                # Present the user with a list of interactive modes to choose from
                mode_choices = [
                    "Load Model",
                    "Listed Queries",
                    "Custom Query",
                    "Add Schema",
                ]
                mode_question = select(
                    "Select an interactive mode:", choices=mode_choices
                ).ask()

                if mode_question == "Add Schema":
                    try:
                        # Create tables in the database schema
                        add_schema_query = queries.create_tables_query()
                        result = self.gemd_db.execute_query(add_schema_query)
                        self.print_and_dump(
                            result, add_schema_query, "add_schema_query"
                        )
                    except Exception as e:
                        print(f"ERROR: {e}")
                        print("Try again.")

                elif mode_question == "Load Model":
                    # Input parameters for loading a model
                    params = input(
                        "Enter the appropriate parameters for loading a model (name and dirpath): "
                    ).ask()
                    params = params.split(" ")
                    self.load_model(params[0], params[1])

                elif mode_question == "Listed Queries":
                    # Display documentation on available queries
                    display_documentation = confirm(
                        "Would you like to display documentation on listed queries?"
                    ).ask()

                    if display_documentation:
                        self.list_queries()

                    # Select a query and specify its required arguments
                    selected_query = input("Enter query with its required arguments: ")
                    selected_query = selected_query.split(" ")
                    identifier = selected_query[0]

                    try:
                        if (
                            identifier in self.listed_acronyms.keys()
                            or identifier.upper() in self.listed_acronyms.keys()
                        ):
                            name = self.listed_acronyms[identifier.upper()]
                            func = self.listed_functions[name][0]
                        elif (
                            identifier in self.listed_functions.keys()
                            or identifier.lower() in self.listed_functions.keys()
                        ):
                            func = self.listed_functions[identifier.lower()][0]
                        else:
                            raise KeyError(
                                f"Couldn't recognize the identifier passed as '{identifier}'. Pass the full name or acronym."
                            )

                        # Execute the selected query
                        selected_query = func(*selected_query[1:])
                        result = self.gemd_db.execute_query(selected_query)
                        self.print_and_dump(result, selected_query, identifier)
                    except Exception as e:
                        print(f"ERROR: {e}")
                        print("Try again.")

                elif mode_question == "Custom Query":
                    # Enter a custom SQL query
                    custom_query = select("Enter a custom query: ").ask()
                    self.logger.info("Executing custom query...")
                    self.logger.info(f"query: {custom_query}")

                    try:
                        result = self.gemd_db.execute_query(custom_query)
                        self.print_and_dump(result, custom_query, "custom_query")
                    except Exception as e:
                        print(f"ERROR: {e}")
                        print("Try again.")
                    self.logger.info("Done.")
        except KeyboardInterrupt:
            pass

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
        open_db.interactive_mode()


def main(args=None):
    """
    Main method to run from command line
    """
    OpenDB.run_from_command_line(args)


if __name__ == "__main__":
    main()
