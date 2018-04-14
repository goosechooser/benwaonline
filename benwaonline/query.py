from benwaonline.mappers import nonempty_fields, relationships

class Query(object):
    def __init__(self, criteria):
        self.criteria = criteria

    def __repr__(self):
        return '<Query {}>'.format(self.criteria)

    def to_filter(self):
        try:
            return [c.to_filter() for c in self.criteria]
        except TypeError:
            return [self.criteria.to_filter()]

class EntityQuery(Query):
    def __init__(self, entity):
        self._criteria = self._load_criteria(entity)

    def __repr__(self):
        return '<EntityQuery {}>'.format(self.criteria)

    def to_filter(self):
        return [self.criteria.to_filter()]

    @property
    def criteria(self):
        return self._criteria

    @criteria.setter
    def criteria(self, entity):
        self._criteria = self._load_criteria(entity)

    def _load_criteria(self, entity):
        fields = nonempty_fields(entity)
        results = [self._field_to_criteria(entity, f) for f in fields]

        if len(results) == 1:
            return results[0]

        return And(results)

    def _field_to_criteria(self, entity, fieldname):
        if fieldname in relationships(entity):
            related_entity = getattr(entity, fieldname)
            return self._relationship_to_criteria(related_entity, fieldname)

        return Criteria('eq', fieldname, getattr(entity, fieldname))

    def _relationship_to_criteria(self, entity, fieldname):
        try:
            return Or([Criteria('any', fieldname, EntityCriteria('eq', f)) for f in entity])
        except TypeError:
            return Criteria('has', fieldname, EntityCriteria('eq', entity))

class Criteria(object):
    def __init__(self, operator, field, value):
        self.operator = operator
        self.field = field
        self.value = value

    def __repr__(self):
        return '<Criteria {} {} {}>'.format(self.operator, self.field, self.value)

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

class EntityCriteria(Criteria):
    def __init__(self, operator, entity):
        self.operator = operator
        self._entity = entity

    def __repr__(self):
        return '<EntityCriteria for entity {}>'.format(type(self._entity))

    def to_filter(self):
        fields = nonempty_fields(self._entity)
        results = [self._field_to_filter(f) for f in fields]

        if len(results) == 1:
            return results[0]

        return results

    def _field_to_filter(self, fieldname):
        if fieldname in relationships(self._entity):
            return self._relationship_to_filter(fieldname)

        return {
            'name': fieldname,
            'op': self.operator,
            'val': getattr(self._entity, fieldname)
        }

    def _relationship_to_filter(self, fieldname):
        field = getattr(self._entity, fieldname)
        try:
            return [Criteria('any', fieldname, EntityCriteria('eq', f).to_filter()).to_filter() for f in field]
        except TypeError:
            return Criteria('has', fieldname, EntityCriteria('eq', field).to_filter()).to_filter()

class Conjunction(object):
    def __init__(self, op, criteria):
        self.op = op
        self.criteria = criteria

    def __repr__(self):
        return '<{} {}>'.format(self.op, self.criteria)

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

