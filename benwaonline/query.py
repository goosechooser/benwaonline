class Query(object):
    def __init__(self, criteria):
        self.criteria = criteria

    def to_filter(self):
        try:
            return [c.to_filter() for c in self.criteria]
        except TypeError:
            return [self.criteria.to_filter()]
            
class Criteria(object):
    def __init__(self, operator, field, value):
        self.operator = operator
        self.field = field
        self.value = value

    def to_filter(self):
        try:
            val = self.value.to_filter()
        except AttributeError:
            val = self.value

        return {
            'name': self.field,
            'op': self.operator,
            'val': val
        }

def eq(field, value):
    return Criteria('eq', field, value)

def any(field, value):
    return Criteria('any', field, value)

class EntityCriteria(Criteria):
    def __init__(self, operator, entity):
        self.operator = operator
        self.entity = entity

    def __repr__(self):
        return '<EntityCriteria for entity {}>'.format(self.entity)

    def to_filter(self):
        fields = self.entity.nonempty_fields()
        results = [self. _field_to_filter(f) for f in fields]

        if len(results) == 1:
            return results[0]

        return results

    def _field_to_filter(self, fieldname):
        if fieldname in self.entity.relationships:
            return self._relationship_to_filter(fieldname)

        return {
            'name': fieldname,
            'op': self.operator,
            'val': getattr(self.entity, fieldname)
        }

    def _relationship_to_filter(self, fieldname):
        field = getattr(self.entity, fieldname)
        try:
            return [Criteria('any', fieldname, EntityCriteria('eq', f).to_filter()).to_filter() for f in field]
        except TypeError:
            return Criteria('has', fieldname, EntityCriteria('eq', field).to_filter()).to_filter()

class Conjunction(object):
    def __init__(self, op, criteria):
        self.op = op
        self.criteria = criteria

    def to_filter(self):
        try:
            return {self.op: [c.to_filter() for c in self.criteria]}
        except TypeError:
            return {self.op: self.criteria.to_filter()}

class Or(Conjunction):
    def __init__(self, criteria):
        super().__init__('or', criteria)

class And(Conjunction):
    def __init__(self, criteria):
        super().__init__('and', criteria)

class Not(Conjunction):
    def __init__(self, criteria):
        super().__init__('not', criteria)

