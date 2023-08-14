import json, glob

from gemd_database import MSSQLDatabase
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from openmsimodel.utilities.runnable import Runnable

from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from openmsimodel.utilities.logging import Logger


class GemdSQL(Runnable):
    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, database_name, private_path):
        with open(private_path, "r") as f:
            self.auth = json.load(f)
        self.database = database_name  # GEMD
        self.gemd_db = MSSQLDatabase(self.auth, self.database)
        self.listed = {
            "show_models": self.show_models,
            "top_elements": self.top_elements,
        }
        self.logger = Logger()

    def execute_query(self, sql):
        self.gemd_db.execute_query(sql)

    def show_models(self):
        """displaying models currently in store"""
        sql = """
        select distinct *
        from GEMDModel
        """
        return self.execute_query(sql)
        # return self.gemd_db.execute_query(sql)

    def top_elements(self, model_id, nb, gemd_type):
        """lists top N elements of certain type"""
        sql = f"""
        select top {nb} context
        from  gemdobject c where gemd_type='{gemd_type} && c.model_id={model_id}' 
        order by newid()
        """
        return self.execute_query(sql)
        # return self.gemd_db.execute_query(sql)

    def prepare_classes(self):
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
        self.logger.info("Loading model...")
        GEMDObject, GEMDModel = self.prepare_classes()

        model = GEMDModel(name=name)

        files = glob.glob(f"{dirpath}/*.json")
        for file in files:
            with open(f"{file}", "r") as f:
                try:
                    d = json.load(f)
                    GEMDObject(
                        gemd_type=d["type"],
                        uid=d["uids"]["auto"],
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
        args = [*superargs, "database_name", "private_path"]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        gemd_sql = cls(args.database_name, args.private_path)
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
                    gemd_sql.load_model(name, dirpath)
                elif mode == "listed":  # listed functions
                    for function_key, function in gemd_sql.listed.items():
                        gemd_sql.logger.info(
                            f"- function name: {function.__name__}, description: {function.__doc__}"
                        )
                    additional_args = input().split()
                    passed_function_key = additional_args[0]
                    if passed_function_key == "show_models":
                        gemd_sql.logger.info(gemd_sql.show_models())
                    elif passed_function_key == "top_elements":
                        # additional_args = input()
                        model_id = additional_args[1]
                        nb = additional_args[2]
                        gemd_type = additional_args[3]
                        gemd_sql.logger.info(
                            gemd_sql.top_elements(model_id, nb, gemd_type)
                        )
                elif mode == "custom":  # custom query
                    sql = " ".join(args[1:])
                    gemd_sql.logger.info("executing custom query...")
                    gemd_sql.logger.info(f"query: {sql}")
                    print(gemd_sql.gemd_db.execute_query(sql))
                    gemd_sql.logger.info("Done.")
        except KeyboardInterrupt:
            pass

        # workflow.build()


def main(args=None):
    """
    Main method to run from command line
    """
    GemdSQL.run_from_command_line(args)


if __name__ == "__main__":
    main()
