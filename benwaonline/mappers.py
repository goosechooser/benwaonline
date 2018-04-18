'''
'''
from typing import List
from marshmallow_jsonapi.fields import Relationship

Entity = 'Entity'

def nonempty_fields(e: Entity) -> List[str]:
    return [v for v in e.schema._declared_fields.keys() if getattr(e, v)]

def relationships(e: Entity) -> List[str]:
    return [k for k, v in e.schema._declared_fields.items() if isinstance(v, Relationship)]

def collection_uri(e: Entity) -> str:
    return e.schema.Meta.self_url_many

def instance_uri(e: Entity) -> str:
    return e.schema.Meta.self_url.replace('{id}', str(e.id))

def resource_uri(e: Entity, resource: str) -> str:
    related_url = e.schema._declared_fields[resource].related_url
    return related_url.replace('{id}', str(e.id))

def relationship_uri(e: Entity, resource: str) -> str:
    self_url = e.schema._declared_fields[resource].self_url
    return self_url.replace('{id}', str(e.id))

def many(e: Entity, resource: str) -> bool:
    return e.schema._declared_fields[resource].many