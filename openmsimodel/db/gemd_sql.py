import json, glob, os, csv
import random
from gemd_database import MSSQLDatabase
from openmsimodel.utilities.argument_parsing import OpenMSIModelParser
from openmsimodel.utilities.runnable import Runnable

from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from openmsimodel.utilities.logging import Logger


class GemdSQL(Runnable):
    ARGUMENT_PARSER_TYPE = OpenMSIModelParser

    def __init__(self, database_name, private_path, destination):
        with open(private_path, "r") as f:
            self.auth = json.load(f)
        self.database = database_name  # GEMD
        self.gemd_db = MSSQLDatabase(self.auth, self.database)
        self.destination = destination
        self.listed = {
            "show_models": self.show_models,
            "top_elements": self.top_elements,
            "display_all": self.display_all,
            "return_all_paths": self.return_all_paths,
        }
        self.logger = Logger()

    def show_models(self):
        """displaying models currently in store"""
        sql = """select distinct * from GEMDModel"""
        return self.gemd_db.execute_query(sql), sql

    def top_elements(self, model_id, nb, gemd_type):
        """lists top N elements of certain type"""
        sql = f"""
        select top {nb} context
        from  gemdobject c where gemd_type='{gemd_type} && c.model_id={model_id}' 
        order by newid()
        """
        return self.gemd_db.execute_query(sql), sql

    def display_all(self, model_id, type_to_display):
        """display all elements of a certain class"""
        sql = f""" select * from {type_to_display} where model_id={model_id}"""
        return self.gemd_db.execute_query(sql), sql

    def return_all_paths(self, model_id):
        """return all paths between all nodes in model"""

        sql = f"""
        with gr as (
        select c.uid as root_uid
        ,      c.gemd_type as root_type
        ,      0 as level
        ,      cast(NULL as varchar(64)) as endpoint_uid
        ,      c.uid as from_uid, cast(NULL as bigint) as edge_id, cast(NULL as varchar(64)) as gemd_ref
        ,      cast(gemd_type+':'+c.uid as varchar(max)) as [path]
        from GEMDObject c where c.model_id={model_id} 
        union all
        select gr.root_uid, gr.root_type, gr.level+1, e.to_uid
        ,      e.to_uid, e.id, e.gemd_ref
        ,      gr.path+'==>'+e.gemd_ref+':'+e.to_uid
        from gr
        join GEMDEdge e on e.from_uid=gr.from_uid
        where gr.level < 16
        )
        select root_uid, root_type, endpoint_uid
        ,      edge_id,gemd_ref
        ,      path, level
        from gr
        order by root_type,root_uid, path
        """
        return self.gemd_db.execute_query(sql), sql

    def print_and_dump(self, sql_results, query, name):
        destination_file = os.path.join(
            self.destination, name + str(random.randint(0, 100000)) + ".csv"
        )
        print(sql_results)
        sql_results.to_csv(destination_file)
        with open(destination_file, "a") as fp:
            w = csv.writer(fp)
            w.writerow("\n")
            w.writerow([query])

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
        args = [*superargs, "database_name", "private_path", "destination"]
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        gemd_sql = cls(args.database_name, args.private_path, args.destination)
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
                        result, query = gemd_sql.show_models()
                        gemd_sql.print_and_dump(result, query, "show_models")
                    elif passed_function_key == "return_all_paths":
                        model_id = additional_args[1]
                        result, query = gemd_sql.return_all_paths(model_id)
                        gemd_sql.print_and_dump(result, query, "return_all_paths")
                    elif passed_function_key == "display_all":
                        model_id = additional_args[1]
                        type_to_display = additional_args[2]
                        result, query = gemd_sql.display_all(model_id, type_to_display)
                        gemd_sql.print_and_dump(result, query, "display_all")
                    elif passed_function_key == "top_elements":
                        model_id = additional_args[1]
                        nb = additional_args[2]
                        gemd_type = additional_args[3]
                        result, query = gemd_sql.top_elements(model_id, nb, gemd_type)
                        gemd_sql.print_and_dump(result, query, "top_elements")
                elif mode == "custom":  # custom query
                    query = " ".join(args[1:])
                    gemd_sql.logger.info("executing custom query...")
                    gemd_sql.logger.info(f"query: {query}")

                    result = gemd_sql.gemd_db.execute_query(query)
                    gemd_sql.print_and_dump(result, query, "custom_query")
                    gemd_sql.logger.info("Done.")
        except KeyboardInterrupt:
            pass


def main(args=None):
    """
    Main method to run from command line
    """
    GemdSQL.run_from_command_line(args)


if __name__ == "__main__":
    main()
