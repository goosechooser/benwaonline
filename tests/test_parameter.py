import pytest
from benwaonline import query
from benwaonline.entities import Post, Tag
from benwaonline.gateways import Parameter

def test_parameter_init():
    params = {
        'page_size': 0,
        'fields': {'user': ['username']}
    }

    expected = {
        'include': 'user,posts',
        'page[size]': 0,
        'fields[user]': 'username',
    }

    p = Parameter(include=['user', 'posts'], **params)
    #requests ignores key with value of None, so just going to filter them out zzz
    result = {k: v for k,v in p.dump().items() if v is not None}
    assert result == expected

@pytest.mark.skip
def test_entity_query():
    tag = Tag(name='hello')
    tag2 = Tag(name='benwa')
    post = Post(tags=[tag, tag2])

    c1 = query.EntityCriteria('any', post)
    q = query.Query(query.Or(c1))
    expected = {
        'filter': '[{"or": [{"name": "tags", "op": "any", "val": {"name": "name", "op": "eq", "val": "hello"}}, {"name": "tags", "op": "any", "val": {"name": "name", "op": "eq", "val": "benwa"}}]}]'
    }
    p = Parameter(filter=q.dumps())
    print(p.dump())
    assert p.dump() == expected