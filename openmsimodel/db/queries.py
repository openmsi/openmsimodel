from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from openmsimodel.utilities.io import read_gemd_data
from gemd.json import GEMDJson
import json

model_table_name = "GEMDModel"
object_table_name = "GEMDObject"
attribute_table_name = "GEMDAttribute"
edge_table_name = "GEMDEdge"


def show_models():
    """shows all models in the database.

    Returns:
        _type_: str
    """
    return """select distinct * from GEMDModel"""


def top_elements(model_id, nb, gemd_type):
    """return top elements of a certain type from model.

    Args:
        model_id (int): id of the model to query
        nb (int): number of elements
        gemd_type (str): type of gemd object

    Returns:
        _type_: str
    """
    return f"""select top {nb} * from gemdobject c where gemd_type='{gemd_type}' AND c.model_id='{model_id}' order by newid()"""


def display_all(model_id, type_to_display):
    """displays all the gemd objects of a certain type in the model.

    Args:
        model_id (int): id of the model to query
        type_to_display (str): object type to display

    Returns:
        _type_: str
    """
    return f""" select * from {type_to_display} where model_id={model_id}"""


def return_all_paths(model_id):
    """return all paths between all nodes in model"""
    return f"""
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


def gemd_types_query():
    return """
    select distinct gemd_type
    ,      x.[key]
    from GEMDObject cross apply openjson(context,'$') x
    where x.[key] not in ('tags','description','uids','name','type','bounds','file_links','labels')
    order by 1,2
    """


def reachable_nodes_query(uid):
    """returns all the elements that can be reached from the node.

    Args:
        uid (str): unique identifier of object to query with

    Returns:
        _type_: str
    """
    return f"""
        with gr as (
        select c.uid as node_uid
        ,      c.gemd_type as node_type
        ,      c.context as node_context
        ,      cast(c.gemd_type+' ['+c.uid+']' as varchar(128)) as Target
        ,      cast(-1 as bigint) as edge_id
        ,      cast(NULL as varchar(64)) as from_uid
        ,      cast(NULL as varchar(128)) as Source
        ,      0 as level
        from GEMDObject c
        where uid='{uid}'
        union all
        select c.uid as node_uid
        ,      c.gemd_type as node_type
        ,      c.context as node_context
        ,      cast(c.gemd_type+' ['+c.uid+']' as varchar(128)) as Target
        ,      e.id as edge_id
        ,      gr.node_uid as from_uid
        ,      gr.Target as Source
        ,      gr.level+1 as level
        from gr
        join GEMDEdge e on e.from_uid=gr.node_uid
        join GEMDObject c on c.uid=e.to_uid
        where gr.level < 16
        )
        select Source,Target,node_context
        --,node_type,node_context
        from gr
        
    """


def to_node_query(model_id):
    """returns all elements that can reach a given node, for all nodes in the model.

    Args:
        model_id (str): id of the model to query from

    Returns:
        _type_: str
    """
    return f"""
        with gr as (
        select c.uid as root_uid
        ,      c.gemd_type as root_type
        ,      0 as level
        ,      cast(NULL as varchar(64)) as endpoint_uid
        ,      c.uid as from_uid, cast(NULL as bigint) as edge_id, cast(NULL as varchar(64)) as gemd_ref
        ,      cast(gemd_type+c.uid as varchar(max)) as [path]
        from GEMDObject c where c.model_id={model_id}
        union all
        select gr.root_uid, gr.root_type, gr.level+1, e.to_uid
        ,      e.to_uid, e.id, e.gemd_ref
        ,      gr.path+'==>'+e.gemd_ref+':'+e.to_uid
        from gr
        join GEMDEdge e on e.from_uid=gr.from_uid
        where gr.level < 16
        )
        select endpoint_uid, count(distinct root_uid) as num_in_nodes
        from gr
        group by endpoint_uid
        order by num_in_nodes desc
    """


def multiple_paths_nodes_query(model_id):
    return f"""
    with gr as (
    select c.uid as root_uid
    ,      c.gemd_type as root_type
    ,      0 as level
    ,      cast(NULL as varchar(64)) as endpoint_uid
    ,      cast(NULL as varchar(32)) as endpoint_type
    ,      c.uid as from_uid, cast(NULL as bigint) as edge_id, cast(NULL as varchar(64)) as gemd_ref
    ,      cast(gemd_type+c.uid as varchar(max)) as [path]
    from GEMDObject c where c.model_id={model_id} AND gemd_type='material_run' 
    union all
    select gr.root_uid, gr.root_type, gr.level+1, e.to_uid, c.gemd_type
    ,      e.to_uid, e.id, e.gemd_ref
    ,      gr.path+'==>'+e.gemd_ref+':'+e.to_uid
    from gr 
    join GEMDEdge e on e.from_uid=gr.from_uid
    join GEMDObject c on c.uid=e.to_uid
    where gr.level < 16
    )
    select root_uid, root_type, endpoint_uid, endpoint_type
    ,      min(path) as path, min(level) as min_level, max(level) as max_level
    ,      count(*) as num_paths
    from gr
    group by root_type, root_uid, endpoint_uid,endpoint_type having count(*) > 1  -- if you want to find multiple paths between nodes
    order by root_type,root_uid, endpoint_uid,path
    """


def return_all_paths(model_id):
    """return all paths between all nodes, if exst.

    Args:
        model_id (str): id of the model to query from

    Returns:
        _type_: str
    """
    return f"""
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


###############################


def create_tables_query():
    """creates a table with the designed GEMD schema."""

    return f"""
    create table {model_table_name} (
        id bigint identity(1,1) not null
    , name varchar(1024) not null
    , constraint  primary key(id)
    )

    create table {object_table_name} (
    uid varchar(64) not null
    , model_id bigint not null
    , gemd_type varchar(32) not null
    , context varchar(max) not null
    , constraint pk_GEMDContext primary key(uid)
    , constraint fk_gemdcontext_model foreign key (model_id) REFERENCES gemdmodel_temp(id)
    )
    
    CREATE TABLE [dbo].[{attribute_table_name}](
    [gemdobject_uid] [varchar](64) NOT NULL,
    [template_id] [nvarchar](128) NULL,
    [name] [nvarchar](128) NULL,
    [value] [nvarchar](4000) NULL,
    [value_type] [nvarchar](32) NULL,
    [value_units] [nvarchar](128) NULL,
    [attribute_type] [nvarchar](128) NULL,
    [property] [nvarchar](max) NULL,
    [conditions] [nvarchar](max) NULL
    )

    CREATE TABLE {edge_table_name}(
        id bigint IDENTITY(1,1)  not null
    , from_uid varchar(64) not null
    , to_uid varchar(64) not null
    , gemd_ref varchar(64) not null
    )
    """


def create_edges_query(model_id):
    """creates and stores 'GEMDEdge's based on pre-existing 'GEMDObject's"""
    return f"""insert into GEMDEdge
    select uid,material_run_uid, 'ingredient_run:material_run'
    from ingredient_run WHERE model_id={model_id} AND material_run_uid is not null
    union
    select uid,process_run_uid, 'ingredient_run:process_run'
    from ingredient_run WHERE model_id={model_id} AND process_run_uid is not null
    union
    select uid,spec_uid, 'ingredient_run:spec'
    from ingredient_run WHERE model_id={model_id} AND process_run_uid is not null
    union
    select uid,process_spec_uid, 'ingredient_spec:process_spec'
    from ingredient_spec WHERE model_id={model_id} AND process_spec_uid is not null
    union
    select uid,material_spec_uid, 'ingredient_spec:material_spec'
    from ingredient_spec WHERE model_id={model_id} AND material_spec_uid is not null
    union
    select uid,spec_uid, 'material_run:spec'
    from material_run WHERE model_id={model_id} AND spec_uid is not null
    union
    select uid, process_run_uid, 'material_run:process_run'
    from material_run WHERE model_id={model_id} AND process_run_uid is not null
    union
    select uid,process_spec_uid, 'material_spec:process_spec'
    from material_spec WHERE model_id={model_id} AND process_spec_uid is not null
    union
    select uid,template_uid, 'material_spec:template'
    from material_spec WHERE model_id={model_id} AND template_uid is not null
    union
    select uid,spec_uid, 'measurement_run:spec'
    from measurement_run WHERE model_id={model_id} AND spec_uid is not null
    union
    select uid,material_uid, 'measurement_run:material'
    from measurement_run WHERE model_id={model_id} AND material_uid is not null
    union
    select uid,template_uid, 'measurement_spec:template'
    from measurement_spec WHERE model_id={model_id} AND template_uid is not null
    union
    select uid,spec_uid, 'process_run:spec'
    from process_run WHERE model_id={model_id} AND spec_uid is not null
    union
    select uid,template_uid, 'process_spec:template'
    from process_spec WHERE model_id={model_id} AND template_uid is not null
    """


def create_attributes_query(model_id):
    return f"""
        with a as (
        select s.uid, s.gemd_type
        ,      sp.*
        from GEMDObject s where model_id={model_id}
        cross apply OPENJSON(s.context,'$.parameters') with (
            template_id nvarchar(128) '$.template.id',
            name nvarchar(128) '$.name',
            value_type nvarchar(max) '$.value.type' ,
            value_units nvarchar(max) '$.value.units' ,
            value nvarchar(max) '$.value' as json,
            attribute_type nvarchar(128) '$.type',
            parameter nvarchar(max) '$' as json) sp
        )
        insert into GEMDAttribute
        select a.uid as gemdcontext_uid, a.template_id, a.name
        ,      case when a.value_type = 'nominal_categorical' then json_value(a.value,'$.category')
                    when a.value_type = 'nominal_real' then json_value(a.value,'$.nominal')
                    when a.value_type = 'nominal_integer' then json_value(a.value,'$.nominal')
                    when a.value_type = 'nominal_composition' then json_value(a.value,'$')
            else NULL end as value
            , a.value_type
            , a.value_units
        ,      a.attribute_type
        ,      a.parameter, NULL
        from a 
    """


def prepare_classes(db_engine):
    try:
        Base = automap_base()
        Base.prepare(db_engine, reflect=True)
        for c in Base.classes:
            print(c)
        GEMDObject = Base.classes.GEMDObject
        GEMDModel = Base.classes.GEMDModel
        return GEMDObject, GEMDModel
    except Exception as e:
        raise e


def load_model_query(name, db, dirpath, uuid):
    """function to load a model into the base

    Args:
        name (str): name of the model
        dirpath (str): path to folder or single file containing JSONs
        uuid (str, optional): _description_.
    """
    print("Loading model and GEMDObjects...")

    GEMDObject, GEMDModel = prepare_classes(db.ENGINE)

    # creating GEMDModels
    model = GEMDModel(name=name)

    # creating GEMDObjects
    files = read_gemd_data(dirpath, GEMDJson())
    for f in files:
        try:
            GEMDObject(
                gemd_type=f["type"],
                uid=f["uids"][uuid][:64],
                context=json.dumps(f),
                gemdmodel=model,
            )
        except Exception as e:
            print("ERROR:", e)

    session = Session(db.ENGINE)
    session.add(model)
    session.commit()
    print("Session commited.")

    # print("Loading GEMDEdges and GEMDAttributes...")
    # # creating GEMDEdges
    # db.execute_query(create_edges_query(model.id))

    # # creating GEMDEdges
    # db.execute_query(create_attributes_query(model.id))

    print("Queries executed.")
