'''
This module is for loading Entities from api responses.
Hopefully it keeps the Entities and their related Schema far, far apart.
'''
from importlib import import_module
from typing import List, Mapping, TypeVar

Entity = 'Entity'
Schema = 'Schema'
E = TypeVar('E', Entity, List[Entity])

def get_entity(e: str) -> Entity:
    '''*shrugs* im lazy'''
    module = import_module('.', package='benwaonline.entities')
    try:
        return getattr(module, _map(e))
    except ImportError:
        print('no entity {} in module {}'.format(_map(e), module))
        return None

def get_schema(s: str) -> Schema:
    module = import_module('.', package='benwaonline.schemas')
    try:
        return getattr(module, s)
    except ImportError:
        print('no schema {} in module {}'.format(s, module))
        return None

def make_entity(e: str, data: dict, many: bool = False) -> E:
    '''Factory method.

    Args:
        e: name of the Entity.
        data: a JSON-API formatted dict.
        many: optional variable, set True if response contains multiple resource objects.
    Returns:
        either a list of Entity instances (if many is True) or a single Entity instance.
    '''
    obj = get_entity(e)
    schema = get_schema(obj._schema)

    data, errors = schema().load(data, many=many)
    if errors:
        msg = 'schema {} produced errors: {}'.format(obj._schema, errors['errors'])
        print(msg)

    return [obj(**d) for d in data] if many else obj(**data)

def _map(e: str) -> str:
    '''Maps string names to Entities'''
    e_map = {
        'likes': 'PostLike',
        'tags': 'Tag',
        'comments': 'Comment',
        'posts': 'Post'
    }
    return e_map.get(e, e.capitalize())

def load_included(main: E, data: dict, included: List[str]):
    included_resources = [from_include(include) for include in data]
    if not isinstance(main, list):
        main = [main]

    includes = map_resources(main[0], included_resources)
    for m in main:
        for field in included:
            load_subresource(m, field.split('.'), includes)

def from_include(include: dict) -> Entity:
    ''' Creates the relevant Entity based on a given entry in the included section'''
    e = include['type'][0:-1]
    data = {'data': include}
    return make_entity(e, data)

def from_response(e: str, r: dict, **kwargs) -> E:
    entity = make_entity(e, r, many=kwargs.get('many', False))
    try:
        load_included(entity, r['included'], kwargs.get('include'))
    except KeyError:
        pass

    return entity

def map_resources(e: Entity, resources: List[Entity]) -> Mapping[str, Entity]:
    mapping = {}
    for resource in resources:
        type_ = e.attrs.get(resource.type_, resource.type_)
        key = '{}__{}'.format(type_, resource.id)
        mapping[key] = resource

    return mapping

def load_subresource(e: Entity, fields: List[str], included: Mapping[str, Entity]) -> Entity:
    ''' Matches an Entity's field to the appropiate Entity(s)

    ex: Comment has a post field -> Comment.post = Post
    ex: Comment has a post field, Post has a preview field -> Post.preview = Preview then Comment.post = Post
    '''
    current_field = fields[0]
    obj_field = getattr(e, e.attrs.get(current_field, current_field))

    try:
        field_entity = get_entity(current_field)(**obj_field)
    except TypeError:
        val = _handle_field(obj_field, current_field, included)
        setattr(e, current_field, val)
        return e

    try:
        val = load_subresource(field_entity, fields[1:], included)
        setattr(e, current_field, val)
    except IndexError:
        pass

    return e

def _handle_field(obj_field: TypeVar('T', str, dict, list), current_field: str, included: Mapping[str, Entity]) -> E:
    if isinstance(obj_field, str):
        key = '{}__{}'.format(current_field, obj_field)
        return included[key]

    if isinstance(obj_field, dict):
        key = '{}__{}'.format(current_field, obj_field['id'])
        return included[key]

    if isinstance(obj_field, list):
        keys = ['{}__{}'.format(current_field, sub['id']) for sub in obj_field]
        return [included[key] for key in keys]
