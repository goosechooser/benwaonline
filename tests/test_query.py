import pytest
from marshmallow import pprint
from benwaonline.entities import User, Tag, Post
from benwaonline.query import Query, Criteria, Or, And, eq, any, EntityCriteria

def test_eq():
    c = eq('username', 'Benwa Benwa Benwa')
    cfilter = c.to_filter()
    assert type(cfilter) == dict

    q = Query(c)
    filters = q.to_filter()
    assert type(filters) == list

def test_or():
    c = eq('username', 'Benwa Benwa Benwa')
    c2 = eq('username', 'Another Benwa Benwa')
    q = Query(Or([c, c2]))

    assert q.to_filter() == [{
        'or': [
            {
                'name': 'username',
                'op': 'eq',
                'val': 'Benwa Benwa Benwa'
            },
            {
                'name': 'username',
                'op': 'eq',
                'val': 'Another Benwa Benwa'
            }
        ]
    }
    ]

def test_and():
    example = [
        {
          "and": [
            {
              "name": "name",
              "op": "like",
              "val": "%Jim%"
            },
            {
              "name": "birth_date",
              "op": "gt",
              "val": "1990-01-01"
            }
          ]
        }
    ]

    c1 = Criteria('like', 'name', '%Jim%')
    c2 = Criteria('gt', 'birth_date', "1990-01-01")
    and_ = And([c1, c2])
    q = Query(and_)

    assert q.to_filter() == example

def test_criteria_contains_criteria():
    example = [
        {
            "name": "computers",
            "op": "any",
            "val":
            {
                "name": "serial",
                "op": "ilike",
                "val": "%Amstrad%"
            }
        }
    ]
    c1 = Criteria('ilike', 'serial', '%Amstrad%')
    c2 = Criteria('any', 'computers', c1)
    q = Query(c2)

    assert q.to_filter() == example

def test_entity_criteria():
    user = User(username='Benwa')
    c1 = EntityCriteria('any', user)
    assert c1.to_filter() == {
        'name': 'username',
        'op': 'any',
        'val': 'Benwa'
    }

def old_tagname_filter(tags):
    split_tags = tags.split('+')
    filters = [
        {
            'name': 'tags',
            'op': 'any',
            'val': {
                'name': 'name',
                'op': 'eq',
                'val': tag
            }
        }
        for tag in split_tags]
    filters = {'or': filters}

    return [filters]

def test_entity_contains_entities():
    tags = 'benwa+nice'
    expected = old_tagname_filter(tags)

    post = Post(tags=[Tag(name='benwa'), Tag(name='nice')])
    c1 = EntityCriteria('any', post)
    q = Query(Or(c1))
    output = q.to_filter()

    pprint(output)
    pprint(expected)
    assert output == expected
