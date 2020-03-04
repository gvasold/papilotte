"""Pony based FactoidConnector.
"""
import datetime

from pony import orm
# This is important as using orm.desc in a query leads to an Exception
from pony.orm import desc

from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.exceptions import CreationException, ReferentialIntegrityError

from . import filter_queries


class FactoidConnector(AbstractConnector):
    """A FactoidConnector using the Pony ORM.
    """

    def __init__(self, connector_configuration):
        self.db = connector_configuration["db"]

    def get(self, obj_id):
        """Return the factoid dict with id factoid_id or None if no such factoid.

        :param obj_id: the id of the source object to return
        :type object_id: string
        :return: The object as defined in the openAPI definition or None
        :rtype: dict
        """
        Factoid = self.db.entities["Factoid"]
        result = None
        with orm.db_session:
            factoid = Factoid.get(id=obj_id)
            if factoid:
                result = factoid.to_ipif()
        return result

    def filter(self, **filters):
        """Return a pony query object with all filters applied.
        # TODO: Discuss if metadata should be searched, too
        """
        Factoid = self.db.entities["Factoid"]
        subquery_person = filter_queries.person_query(self.db, **filters)
        subquery_source = filter_queries.source_query(self.db, **filters)
        subquery_statement = filter_queries.statement_query(self.db, **filters)
        subquery_factoid = filter_queries.factoid_query(self.db, **filters)
        query = orm.select(f for f in Factoid
            if f in subquery_factoid
#                for f in p.factoids
                if (f.person in subquery_person
                    and f.source in subquery_source)
                    for stmt in f.statements 
                        if stmt in subquery_statement
        )
        return query

    @orm.db_session
    def search(self, size, page, sort_by="createdWhen", sort_order="ASC", **filters):
        """Find all objects which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of factoid.

        :param size: the number of results per page.
        :type size: int
        :param page: the number of the result page, starting with 1 (first page).
        :type page: int
        :param sort_by: the field the output should be sorted by. Default is 'createdWhen'.
                        It is suggegested to alway use '@id' as as second sort field, to
                        keep result order consistent for paging.
        :type sort_by: str
        :return: a list of factoid objects (represented as dictionaries)
        :rtype: list
        """
        Factoid = self.db.entities["Factoid"]
        if sort_by == "@id":
            sort_by = "id"
        with orm.db_session:
            if filters:
                # TODO: replace datetime by anything which can handle dates bc
                if "from_" in filters:
                    filters["from_"] = datetime.date.fromisoformat(filters["from_"])
                if "to" in filters:
                    filters["to"] = datetime.date.fromisoformat(filters["to"])
                query = self.filter(**filters)
            else:
                query = orm.select(f for f in Factoid)

            # TODO: specifiy sort order values in spec. Sorting by uris should be excluded in
            # spec (needs discussion)

            # set descending order if necessary and add id as second sort field (if not first)
            if sort_order.lower() == "desc":
                sort_expression = "desc(f.{}), f.id".format(sort_by)
                query = query.sort_by(sort_expression)
            else:
                if sort_by == "id":
                    sort_expression = "f.id"
                else:
                    sort_expression = "f.{}, f.id".format(sort_by)
                query = query.sort_by(sort_expression)
            result = [f.to_ipif() for f in query.page(page, size)]
        return result


    def count(self, **filters):
        """Return the number of factoids matching the filters.
        :param **filters: a **kwargs containing any number of filter parameters
        :type **filters: dict
        :return: the number of factoids found
        :rtype: int
        """
        Factoid = self.db.entities["Factoid"]
        with orm.db_session:
            if filters:
                query = self.filter(**filters)
            else:
                query = orm.select(s for s in Factoid)
            result= query.count()
        return result

    def create(self, data):
        """Create a new Factoid.
        """
        Factoid = self.db.entities["Factoid"]
        # FIXME: there seems to be an inconsisteny in the spec: in model each factoid only can have one statement,
        #       but in refs statements is a list. As I need a running version quickly, I follow the actual spec
        #       and put the single statement into a list before saving.
        if 'statement' in data:
            stmt = data.pop('statement')
            data['statements'] = [stmt]
        try:
            with orm.db_session:
                factoid = Factoid.create_from_ipif(data)
                result = factoid.to_ipif()
            return result
        except orm.TransactionIntegrityError:
            raise CreationException(
                "A factoid with id '{}' already exists.".format(data["@id"])
            )

    def update(self, obj_id, data):
        """
        Update or created an object specified by obj_id.
        """
        Factoid = self.db.entities["Factoid"]
        # FIXME: there seems to be an inconsisteny in the spec: in model each factoid only can have one statement,
        #       but in refs statements is a list. As I need a running version quickly, I follow the actual spec
        #       and put the single statement into a list before saving.
        if 'statement' in data:
            stmt = data.pop('statement')
            data['statements'] = [stmt]
        with orm.db_session:
            factoid = Factoid.get_for_update(id=obj_id)
            if factoid is None:
                data['@id'] = obj_id
                factoid = Factoid.create_from_ipif(data)
            else:
                factoid.update_from_ipif(data)
            result = factoid.to_ipif()
        return result

    def delete(self, obj_id):
        """
        Delete factoid with id `obj_id`.
        """
        Factoid = self.db.entities["Factoid"]
        try:
            with orm.db_session:
                Factoid[obj_id].delete()
        except orm.ConstraintError:
            with orm.db_session:
                factoid = Factoid[obj_id]
            msg = (
                "Factoid '{}' cannot be deleted because it is used by at "
                "least one factoid ({})."
            ).format(obj_id, [s.id for s in factoid.factoids][0])
            raise ReferentialIntegrityError(msg)
