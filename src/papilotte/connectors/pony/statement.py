"""Pony based StatementConnector.
"""
import datetime

from pony import orm
# This is important as using orm.desc in a query leads to an Exception
from pony.orm import desc

from papilotte.connectors.abstractconnector import AbstractConnector
from papilotte.exceptions import CreationException, ReferentialIntegrityError

from . import filter_queries


class StatementConnector(AbstractConnector):
    """A StatementConnector using the Pony ORM.
    """

    def __init__(self, connector_configuration):
        self.db = connector_configuration["db"]

    def get(self, obj_id):
        """Return the statement dict with id statement_id or None if no such statement.

        :param obj_id: the id or uri of the statement object to return
        :type object_id: string
        :return: The object as defined in the openAPI definition or None
        :rtype: dict
        """
        result = None
        Statement = self.db.entities["Statement"]
        with orm.db_session:
            statement = Statement.get(id=obj_id)
            if statement is None:
                query = Statement.select(lambda st: obj_id in st.uris.uri)
                statement = query.first()
            if statement:
                result = statement.to_ipif()
                result.pop('Factoid', None)
        return result

    def filter(self, **filters):
        """Return a pony query object with all filters applied.
        # TODO: Discuss if metadata should be searched, too
        """
        Statement = self.db.entities["Statement"]
        subquery_person = filter_queries.person_query(self.db, **filters)
        subquery_source = filter_queries.source_query(self.db, **filters)
        subquery_statement = filter_queries.statement_query(self.db, **filters)
        subquery_factoid = filter_queries.factoid_query(self.db, **filters)
        query = orm.select(s for s in Statement
            if s in subquery_statement
                if (s.factoid in subquery_factoid
                    and s.factoid.person in subquery_person
                    and s.factoid.source in subquery_source)
        )
        return query

    def search(self, size, page, sort_by="createdWhen", sort_order="ASC", **filters):
        """Find all objects which match the filter conditions set via
        filters.

        The filter conditions are defined in the openapi spec of statement.

        :param size: the number of results per page.
        :type size: int
        :param page: the number of the result page, starting with 1 (first page).
        :type page: int
        :param sort_by: the field the output should be sorted by. Default is 'createdWhen'.
                        It is suggegested to alway use '@id' as as second sort field, to
                        keep result order consistent for paging.
        :type sort_by: str
        :return: a list of statement objects (represented as dictionaries)
        :rtype: list
        """
        Statement = self.db.entities["Statement"]
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
                query = orm.select(s for s in Statement)

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
        """Return the number of statements matching the filters.
        :param **filters: a **kwargs containing any number of filter parameters
        :type **filters: dict
        :return: the number of statements found
        :rtype: int
        """
        Statement = self.db.entities["Statement"]
        with orm.db_session:
            if filters:
                query = self.filter(**filters)
            else:
                query = orm.select(s for s in Statement)
            result = query.count()
        return result

    def create(self, data):
        """Create a new Statement.
        """
        Statement = self.db.entities["Statement"]
        try:
            with orm.db_session:
                statement = Statement.create_from_ipif(data)
                result = statement.to_ipif()
            return result
        except orm.TransactionIntegrityError:
            raise CreationException(
                "A statement with id '{}' already exists.".format(data["@id"])
            )

    def update(self, obj_id, data):
        """
        Update or created an object specified by obj_id.
        """
        Statement = self.db.entities["Statement"]
        with orm.db_session:
            statement = Statement.get_for_update(id=obj_id) or Statement(id=obj_id)
            statement.update_from_ipif(data)
            result = statement.to_ipif()
        return result

    @orm.db_session
    def delete(self, obj_id):
        """
        Delete statement with id `obj_id`.
        """
        Statement = self.db.entities["Statement"]
        try:
            with orm.db_session:
                Statement[obj_id].delete()
        except orm.ConstraintError:
            with orm.db_session:
                source = Statement[obj_id]
                msg = (
                    "Statement '{}' cannot be deleted because it is used by at "
                    "least one factoid ({})."
                ).format(obj_id, [s.id for s in source.factoids][0])
            raise ReferentialIntegrityError(msg)
