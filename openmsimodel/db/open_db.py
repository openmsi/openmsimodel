"""
OpenDB - Database Interaction Tool
==================================

OpenDB is a command-line tool that allows interaction with a database for managing model artifacts. It provides capabilities for loading models, executing queries, and more.

Usage:
    python open_db.py [options]

Options:
    --database_name=<name>       Name of the database to connect to.
    --private_path=<path>       Path to a JSON file containing database credentials.
    --output=<path>             Path to the output directory.

Example:
    python open_db.py --database_name=GEMD_DB --private_path=credentials.json --output=output_dir

"""

import json
import random
import time
import os
from pathlib import Path
import pandas as pd

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
    """
    OpenDB - Database Interaction Tool

    This tool allows interaction with a database for managing model artifacts. It provides capabilities for loading models, executing queries, and more.
    """

    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, database_name, private_path, output, source=None, science_kit=None):
        """
        Initialization of OpenDB instance.

        :param database_name: Name of the database to connect to.
        :type database_name: str
        :param private_path: Path to a JSON file containing database credentials.
        :type private_path: str
        :param output: Path to the output directory.
        :type output: str
        """
        self.auth = None
        self.gemd_db = None
        self.source = source
        self.output = output
        self.listed_functions = {}
        self.listed_acronyms = {}
        self.logger = Logger()
        self.science_kit = science_kit
        if self.science_kit:
            self.science_kit.open_dbs[database_name] = self
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
        try:
            for function_name, function in getmembers(queries, isfunction):
                acc = create_acronym(function_name)
                self.listed_acronyms[acc] = function_name
                self.listed_functions[function_name] = (function, acc)
        except Exception as e:
            print(f"Error while reading functions from 'queries': {e}")

    def load_model(self, name, dirpath, uuid="auto"):
        return queries.load_model_query(name, self.gemd_db, dirpath, uuid)

    def create_tables(self):
        return queries.create_tables_query()

    def record_query_results(self, sql_results, query, name, dump=True):
        """
        Print query results and optionally save them to a CSV file.

        :param sql_results: The results of the SQL query.
        :type sql_results: DataFrame
        :param query: The SQL query that produced the results.
        :type query: str
        :param name: A name to use for the output file.
        :type name: str
        :param dump: If True, save the results to a CSV file. Default is True.
        :type dump: bool

        :return: The input DataFrame (sql_results).
        :rtype: DataFrame

        :raises ValueError: If an error occurs while saving to the output file.

        :examples:

        Example 1:

        .. code-block:: python

            result_df = self.load_model("example_model", "/path/to/model")
            query = "SELECT * FROM data"
            self.print_and_dump(result_df, query, "data_output")
        """
        print(f"Query: {query}")

        timestamp = time.strftime("%m%d%Y_%H%M_", time.localtime())
        random_suffix = random.randint(0, 10000)
        output_file = os.path.join(
            self.output, f"{name}_{timestamp}{random_suffix}.csv"
        )

        print(sql_results)

        try:
            if dump:
                sql_results.to_csv(output_file, index=False)
                print(f"Results saved to '{output_file}'")
            else:
                print("Results not saved to a file.")
        except Exception as e:
            error_message = f"Error saving results to '{output_file}': {e}"
            print(error_message)
            raise ValueError(error_message)

        return sql_results

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

    def custom_query(self, query):
        return self.gemd_db.execute_query(query)
    
    def dump_gemd_from_query(self, query_result_path, column_name):
        if not os.path.exists(query_result_path):
            raise ValueError(f"File '{query_result_path}' doesn't exist.")

        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(query_result_path)

        # Check if the column exists
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' does not exist in the CSV file.")

        # Iterate over each row in the specified column
        for index, row in df.iterrows():
            json_data = row[column_name]
            
            # Convert the JSON data to a Python dictionary
            try:
                json_object = json.loads(json_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for row {index}: {e}")
                continue
            
            # Define the output file path
            output_file_path = os.path.join(self.source, f'row_{index}.json')
            
            # Save the JSON object to a file
            with open(output_file_path, 'w') as json_file:
                json.dump(json_object, json_file, indent=4)

            print(f"Saved JSON object from row {index} to {self.source}")


    def interactive_mode(self):
        try:
            while True:
                # Present the user with a list of interactive modes to choose from
                mode_choices = [
                    "Load Model",
                    "Listed Queries",
                    "Custom Query",
                    "Dump from Query To GEMD Folder",
                    "Sync GEMD Folder With Database Table",
                    "Add Schema",
                    "Edit Db: Add Measurement",
                    "Return"
                ]
                mode_question = select(
                    "Select an interactive mode:", choices=mode_choices
                ).ask()

                if mode_question == "Add Schema":
                    try:
                        # Create tables in the database schema
                        add_schema_query = queries.create_tables_query()
                        result = self.gemd_db.execute_query(add_schema_query)
                        self.record_query_results(
                            result, add_schema_query, "add_schema_query"
                        )
                    except Exception as e:
                        print(f"ERROR: {e}")
                        print("Try again.")

                elif mode_question == "Load Model":
                    # Input parameters for loading a model
                    params = input(
                        "Enter the appropriate parameters for loading a model (name and dirpath): "
                    )
                    params = params.split(" ")
                    if len(params) != 2:
                        raise ValueError("Expected two parameters (name and dirpath).")
                    self.load_model(params[0], params[1])

                elif mode_question == "Listed Queries":
                    # Display documentation on available queries
                    display_documentation = confirm(
                        "Would you like to display documentation on listed queries?"
                    ).ask()

                    if display_documentation:
                        self.list_queries()

                    try:
                        # Select a query and specify its required arguments
                        selected_query = input(
                            "Enter query with its required arguments: "
                        )
                        selected_query = selected_query.split(" ")
                        identifier = selected_query[0]

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
                        self.record_query_results(result, selected_query, identifier)
                    except Exception as e:
                        print(f"ERROR: {e}")
                        print("Try again.")

                elif mode_question == "Custom Query":
                    # Enter a custom SQL query
                    custom_query = input("Enter a custom query: ")
                    self.logger.info("Executing custom query...")
                    self.logger.info(f"query: {custom_query}")

                    try:
                        # result = self.gemd_db.execute_query(custom_query)
                        result = self.custom_query(custom_query)
                        self.record_query_results(result, custom_query, "custom_query")
                    except Exception as e:
                        print(f"ERROR: {e}")
                        print("Try again.")
                    self.logger.info("Done.")
                elif mode_question == "Dump from Query To GEMD Folder":
                    # Input parameters for loading a model
                    params = input(
                        "Enter the appropriate parameters for loading a model (path to query result, and column name): "
                    )
                    params = params.split(" ")
                    if len(params) != 2:
                        raise ValueError("Expected two parameters (name and dirpath).")
                    self.dump_gemd_from_query(params[0], params[1])

                elif mode_question == "Return":
                    break

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
