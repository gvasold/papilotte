"""Pony based PersonConnector.
"""
import datetime

from pony import orm
# This is important as using orm.desc in a query leads to an Exception
from pony.orm import desc

from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.exceptions import CreationException, ReferentialIntegrityError

from . import filter_queries


class PersonConnector(AbstractConnector):
    """A PersonConnector using the Pony ORM.
    """

    def __init__(self, connector_configuration):
        self.db = connector_configuration["db"]

    def get(self, obj_id):
        """Return the person dict with id person_id or None.

        :param obj_id: the id or uri of the person object to return
        :type object_id: string
        :return: The object as defined in the openAPI definition or None
        :rtype: dict
        """
        result = None
        with orm.db_session:
            Person = self.db.entities["Person"]
            person = Person.get(lambda p: p.id == obj_id or obj_id in p.uris.uri)
            if person:
                result = person.to_ipif()
        return result

    def filter(self, **filters):
        """Return a pony query object with all filters applied.
        # TODO: Discuss if metadata should be searched, too
        """
        Person = self.db.entities["Person"]
        #with orm.db_session:
        subquery_person = filter_queries.person_query(self.db, **filters)
        subquery_source = filter_queries.source_query(self.db, **filters)
        subquery_statement = filter_queries.statement_query(self.db, **filters)
        subquery_factoid = filter_queries.factoid_query(self.db, **filters)
        query = orm.select(p for p in Person
            if p in subquery_person
                for f in p.factoids
                    if (f in subquery_factoid
                        and f.source in subquery_source)
                    for stmt in f.statements 
                        if stmt in subquery_statement
        )
        return query

    def search(self, size, page, sort_by="createdWhen", sort_order="ASC", **filters):
        """Find all objects which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of
        person.

        :param size: the number of results per page.
        :type size: int
        :param page: the number of the result page, starting with 1 (first page).
        :type page: int
        :param sort_by: the field the output should be sorted by. Default is 'createdWhen'.
                        It is suggegested to alway use '@id' as as second sort field, to
                        keep result order consistent for paging.
        :type sort_by: str
        :return: a list of person objects (represented as dictionaries)
        :rtype: list
        """
        Person = self.db.entities["Person"]
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
                with orm.db_session:
                    query = orm.select(p for p in Person)

            # TODO: specifiy sort order values in spec. Sorting by uris should be excluded in
            # spec (needs discussion)

            # set descending order if necessary and add id as second sort field (if not first)
            if sort_order.lower() == "desc":
                sort_expression = "desc(p.{}), p.id".format(sort_by)
                query = query.sort_by(sort_expression)
            else:
                if sort_by == "id":
                    sort_expression = "p.id"
                else:
                    sort_expression = "p.{}, p.id".format(sort_by)
                query = query.sort_by(sort_expression)
            result = [p.to_ipif() for p in query.page(page, size)]
        return result

    def count(self, **filters):
        """Return the number of persons matching the filters.
        :param **filters: a **kwargs containing any number of filter parameters
        :type **filters: dict
        :return: the number of persons found
        :rtype: int
        """
        Person = self.db.entities["Person"]
        with orm.db_session:
            if filters:
                query = self.filter(**filters)
            else:
                query = orm.select(p for p in Person)
            result = query.count()
        return result

    def create(self, data):
        """Create a new Person.
        """
        Person = self.db.entities["Person"]
        try:
            with orm.db_session:
                person = Person.create_from_ipif(data)
                result = person.to_ipif()
            return result
        except orm.TransactionIntegrityError:
            raise CreationException(
                "A person with id '{}' already exists.".format(data["@id"])
            )

    def update(self, obj_id, data):
        """
        Update or created an object specified by obj_id.
        """
        Person = self.db.entities["Person"]
        with orm.db_session:
            person = Person.get_for_update(id=obj_id) or Person(id=obj_id)
            person.update_from_ipif(data)
            result = person.to_ipif()
        return result

    def delete(self, obj_id):
        """
        Delete person with id `obj_id`.
        """
        Person = self.db.entities["Person"]
        with orm.db_session:
            try:
                Person[obj_id].delete()
            except orm.ConstraintError:
                person = Person[obj_id]
                msg = (
                    "Person '{}' cannot be deleted because it is used by at "
                    "least one factoid ({})."
                ).format(obj_id, [p.id for p in person.factoids][0])
                raise ReferentialIntegrityError(msg)
