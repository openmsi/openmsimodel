import json, glob, os, csv
import random, pathlib

from openmsimodel.db.gemd_database import MSSQLDatabase
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from openmsimodel.utilities.runnable import Runnable
from openmsimodel.utilities.tools import read_gemd_data
from openmsimodel.utilities.logging import Logger
import openmsimodel.db.queries as queries

from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from gemd.json import GEMDJson

from inspect import getmembers, isfunction


def create_acronym(phrase):
    acronym = ""
    words = phrase.split("_")
    for word in words:
        acronym += word[0].upper()
    return acronym


class OpenDB(Runnable):
    """Class to interact with model artefacts in a database, allowing long-term storage of assets, faster and richer data retrieval, etc.
    The module typically extract knowledges directly from JSONs of GEMD objects, and maps the GEMD Json structure to SQL classes (see prepare_classes()).
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

    def print_and_dump(self, sql_results, query, name):
        """_summary_

        Args:
            sql_results (_type_): _description_
            query (_type_): _description_
            name (_type_): _description_
        """
        output_file = os.path.join(
            self.output, name + str(random.randint(0, 100000)) + ".csv"
        )
        print(sql_results)
        sql_results.to_csv(output_file)
        with open(output_file, "a") as fp:
            w = csv.writer(fp)
            w.writerow("\n")
            w.writerow([query])

    def prepare_classes(self):
        """preparing the SQL classes to be used to match the GEMD classes"""
        try:
            Base = automap_base()
            Base.prepare(self.gemd_db.ENGINE)
            for c in Base.classes:
                print(c)
            GEMDObject = Base.classes.GEMDObject
            GEMDModel = Base.classes.GEMDModel
            return GEMDObject, GEMDModel
        except Exception as e:
            print(e)

    def load_model(self, name, dirpath):
        """function to load a model into the base

        Args:
            name (str): name of the model
            dirpath (str): path to folder or single file containing JSONs
        """
        self.logger.info("Loading model...")
        GEMDObject, GEMDModel = self.prepare_classes()

        model = GEMDModel(name=name)

        files = read_gemd_data(dirpath, GEMDJson())
        # files = glob.glob(f"{dirpath}/*.json")
        for file in files:
            # with open(f"{file}", "r") as f:
            try:
                # d = json.load(file)
                d = file
                # print(len(d["uids"]["citrine-demo"]))
                # exit()
                GEMDObject(
                    gemd_type=d["type"],
                    uid=d["uids"]["citrine-demo"][:64],
                    context=json.dumps(d),
                    gemdmodel=model,
                )
            except Exception as e:
                print("ERROR:", file)
                print(e)

        session = Session(self.gemd_db.ENGINE)
        session.add(model)
        session.commit()
        self.logger.info("Session commited.")

    def create_schema(self):
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
        # open_db.load_model(
        #     "cake",
        #     pathlib.Path(
        #         "/srv/hemi01-j01/openmsimodel/examples/bake/example_gemd_material_history.json"
        #     ),
        # )
        try:
            while True:
                args = input().split()
                if len(args) == 0:
                    raise Exception("No arguments passed.")
                mode = args[0]
                if mode == "schema":  # create schema
                    pass
                elif mode == "load":  # load model
                    name = args[1]
                    dirpath = args[2]
                    open_db.load_model(name, dirpath)
                elif mode == "listed":  # listed_functions functions
                    for function_name, (
                        function,
                        function_accronym,
                    ) in open_db.listed_functions.items():
                        open_db.logger.info(
                            f"-  name: {function_name}, acronym: {function_accronym}, description: {function.__doc__} "
                        )
                    additional_args = input().split()
                    identifier = additional_args[0]
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
                    query = func(*additional_args[1:])
                    result = open_db.gemd_db.execute_query(query)
                    open_db.print_and_dump(result, query, identifier)
                elif mode == "custom":  # custom query
                    query = " ".join(args[1:])
                    open_db.logger.info("executing custom query...")
                    open_db.logger.info(f"query: {query}")

                    result = open_db.gemd_db.execute_query(query)
                    open_db.print_and_dump(result, query, "custom_query")
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
