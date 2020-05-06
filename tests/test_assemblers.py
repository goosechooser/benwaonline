import pytest
from benwaonline.entities import User
from benwaonline.schemas import UserSchema
from benwaonline.assemblers import get_entity, get_schema

def test_get_entity():
    assert issubclass(get_entity('user'), User)

def test_get_schema():
    assert issubclass(get_schema(User._schema), UserSchema)



