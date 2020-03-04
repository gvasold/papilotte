"""Pony based SourceConnector.
"""
import datetime

from pony import orm
# This is important as using orm.desc in a query leads to an Exception
from pony.orm import desc

from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.exceptions import CreationException, ReferentialIntegrityError

from . import filter_queries


class SourceConnector(AbstractConnector):
    """A SourceConnector using the Pony ORM.
    """

    def __init__(self, connector_configuration):
        self.db = connector_configuration["db"]

    def get(self, obj_id):
        """Return the source dict with id source_id or None if no such source.

        :param obj_id: the id or uri of the source object to return
        :type object_id: string
        :return: The object as defined in the openAPI definition or None
        :rtype: dict
        """
        Source = self.db.entities["Source"]
        result = None
        with orm.db_session:
            source = Source.get(lambda s: s.id == obj_id or obj_id in s.uris.uri)
            if source:
                result = source.to_ipif()
        return result

    def filter(self, **filters):
        """Return a pony query object with all filters applied.
        # TODO: Discuss if metadata should be searched, too
        """
        Source = self.db.entities["Source"]
        subquery_source = filter_queries.source_query(self.db, **filters)
        subquery_person = filter_queries.person_query(self.db, **filters)
        subquery_statement = filter_queries.statement_query(self.db, **filters)
        subquery_factoid = filter_queries.factoid_query(self.db, **filters)
        query = orm.select(s for s in Source
            if s in subquery_source
                for f in s.factoids
                    if (f in subquery_factoid
                        and f.person in subquery_person)
                    for stmt in f.statements 
                        if stmt in subquery_statement
        )
        return query


    def search(self, size, page, sort_by="createdWhen", sort_order="ASC", **filters):
        """Find all objects which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of source.

        :param size: the number of results per page.
        :type size: int
        :param page: the number of the result page, starting with 1 (first page).
        :type page: int
        :param sort_by: the field the output should be sorted by. Default is 'createdWhen'.
                        It is suggegested to alway use '@id' as as second sort field, to
                        keep result order consistent for paging.
        :type sort_by: str
        :return: a list of source objects (represented as dictionaries)
        :rtype: list
        """
        Source = self.db.entities["Source"]
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
                query = orm.select(s for s in Source)

            # TODO: specifiy sort order values in spec. Sorting by uris should be excluded in
            # spec (needs discussion)

            # set descending order if necessary and add id as second sort field (if not first)
            if sort_order.lower() == "desc":
                sort_expression = "desc(s.{}), s.id".format(sort_by)
                query = query.sort_by(sort_expression)
            else:
                if sort_by == "id":
                    sort_expression = "s.id"
                else:
                    sort_expression = "s.{}, s.id".format(sort_by)
                query = query.sort_by(sort_expression)
            result = [s.to_ipif() for s in query.page(page, size)]
        return result

    def count(self, **filters):
        """Return the number of sources matching the filters.
        :param **filters: a **kwargs containing any number of filter parameters
        :type **filters: dict
        :return: the number of sources found
        :rtype: int
        """
        Source = self.db.entities["Source"]
        with orm.db_session:
            if filters:
                query = self.filter(**filters)
            else:
                query = orm.select(s for s in Source)
            result = query.count()
        return result

    def create(self, data):
        """Create a new Source.
        """
        Source = self.db.entities["Source"]
        try:
            with orm.db_session:
                source = Source.create_from_ipif(data)
                result = source.to_ipif()
            return result
        except orm.TransactionIntegrityError:
            raise CreationException(
                "A source with id '{}' already exists.".format(data["@id"])
            )

    def update(self, obj_id, data):
        """
        Update or created an object specified by obj_id.
        """
        Source = self.db.entities["Source"]
        with orm.db_session:
            source = Source.get_for_update(id=obj_id) or Source(id=obj_id)
            source.update_from_ipif(data)
            result = source.to_ipif()
        return result

    def delete(self, obj_id):
        """
        Delete source with id `obj_id`.
        """
        Source = self.db.entities["Source"]
        with orm.db_session:
            try:
                Source[obj_id].delete()
            except orm.ConstraintError:
                source = Source[obj_id]
                msg = (
                    "Source '{}' cannot be deleted because it is used by at "
                    "least one factoid ({})."
                ).format(obj_id, [s.id for s in source.factoids][0])
                raise ReferentialIntegrityError(msg)
