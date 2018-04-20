import pytest
from benwaonline import mappers
from benwaonline.entities import Tag

@pytest.mark.parametrize('fct, uri', [
    (mappers.collection_uri, '/api/tags'),
    (mappers.instance_uri, '/api/tags/1'),
])
def test_entity_uri(fct, uri):
    tag = Tag(id=1)
    assert fct(tag) == uri

@pytest.mark.parametrize('fct, uri', [
    (mappers.relationship_uri, '/api/tags/1/relationships/posts'),
    (mappers.resource_uri, '/api/tags/1/posts')
])
def test_other_uri(fct, uri):
    tag = Tag(id=1)
    resource = 'posts'
    assert fct(tag, resource) == uri
