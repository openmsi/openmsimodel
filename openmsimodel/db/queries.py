def show_models():
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
    return f"""
    select top {nb} context
    from  gemdobject c where gemd_type='{gemd_type} && c.model_id={model_id}' 
    order by newid()
    """


def display_all(model_id, type_to_display):
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


def create_tables_query():
    # gemd_model_table_name = "GEMDModel"
    # gemd_object_table_name = "GEMDObject"
    # gemd_attribute_table_name = "GEMDAttribute"
    return """
    create table GEMDModel (
        id bigint identity(1,1) not null
    , name varchar(1024) not null
    , constraint pk_gemdmodel primary key(id)
    )

    create table GEMDObject (
    uid varchar(64) not null
    , model_id bigint not null
    , gemd_type varchar(32) not null
    , context varchar(max) not null
    , constraint pk_GEMDContext primary key(uid)
    , constraint fk_gemdcontext_model foreign key (model_id) REFERENCES gemdmodel_temp(id)
    )
    
    CREATE TABLE [dbo].[GEMDAttribute_temp](
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

    CREATE TABLE GEMDEdge(
        id bigint IDENTITY(1,1)  not null
    , from_uid varchar(64) not null
    , to_uid varchar(64) not null
    , gemd_ref varchar(64) not null
    )
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
        select Source,Target
        --,node_type,node_context
        from gr
        where Source is not null
    """


def to_node_query(model_id):
    """returns all elements that can reach a given node, for all nodes in the model.

    Args:
        model_id (str): id of the model to query

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
