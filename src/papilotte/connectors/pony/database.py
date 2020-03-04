"""Pony based database module.

Defines the ORM-Classes in function define_entities.
Provides a make_db() function which returns a configured
pony database object.
"""
import copy
import datetime
import time
import hashlib
import json
import logging
import re

from pony import orm
logger = logging.getLogger(__name__)

def fix_datetime(dt):
    """Return a datetime like object pony can deal with.

    Pony does not like iso with timezone set, so we try to convert to UTC (does not repespect summer time yet).
    For the moment I do not have enough time to com eup with a clean solution, because summer time,
    So for the time beeing all I do is to strip timezon information.
    Pony also expects None for missing datetimes.
    """
    #FIXME: there must be a better way to get rid of the zimezone info (pony cannot handle this)
    if dt == '':
        dt = ''#None
    else:
        m = re.match(r'(.*)([+\-])(\d{2}):(\d{2})', dt)
        if m:
            dt = datetime.datetime.fromisoformat(m.group(1)).isoformat(timespec='seconds')
            # simple_dt = datetime.datetime.utcfromtimestamp(m.group(1))
            # operation = m.group(2)
            # delta = datetime.timedelta(hours=int(m.group(3)), minutes=int(m.group(4)))
            # if operation == '-':
            #     dt = simple_dt + delta
            # else:
            #     dt = simple_dt - delta
       # utc_ts = time.mktime(datetime.datetime.fromisoformat(dt).utctimetuple())
       # dt = datetime.datetime.utcfromtimestamp(utc_ts)
       # dt = dt.isoformat(timespec='seconds')
    return dt

class IPIFMixin:
    "Generic mixin class for dealing with IPIF conform data"

    @classmethod
    def create_from_ipif(cls, ipif_data):
        """Create a new ORM object from ipif_data.

        If '@id' is set, this will be respected; otherwise an id will be generated.
        """
        data = copy.deepcopy(ipif_data)
        obj_id = data.pop("@id") if "@id" in data else cls.make_id(data)

        # we use update() for setting data to have code in a single place
        orm_obj = cls(id=obj_id)
        orm_obj.update_from_ipif(data)
        return orm_obj

    def to_ipif(self):
        "Return a ORM object as IPIF-conform dictionary."
        data = self.to_dict()
        data["@id"] = data.pop("id")
        if data.get("createdWhen"):
            data["createdWhen"] = data["createdWhen"].isoformat()
        else:
            data["createdWhen"] = ""
        if data.get("modifiedWhen"):
            data["modifiedWhen"] = data["modifiedWhen"].isoformat()
        else:
            data["modifiedWhen"] = ""
        data["uris"] = sorted([uri.to_ipif() for uri in self.uris])

        refs = []
        for factoid in self.factoids:
            refs.append(factoid.get_refs())
        refs.sort(key=lambda f: f['@id'])
        data["factoid-refs"] = refs
        return data

    @classmethod
    def make_id(cls, data, extra=""):
        """Generate a string id based on the hashed data.
        Try to keep it short.
        """
        d_str = json.dumps(data, default=str).encode("utf-8")
        d_str += extra.encode("utf-8")
        full_hash = hashlib.sha256(d_str).hexdigest()
        for i in range(4, len(full_hash)):
            if cls.get(id=full_hash[:i]) is None:
                return full_hash[:i]
        # if we did not find an unused id, we add the current timestamp and retry
        return cls.make_id(data, datetime.datetime.now().isoformat())


class LabelUriMixin:
    "Mixin class for all entities existing of uri and label"

    @classmethod
    def get_or_create(cls, label="", uri=""):
        """Return an object with this combination of label and uri.
        If no such object exists, it will be created.
        """
        role = cls.get(label=label, uri=uri)
        if not role:
            role = cls(label=label, uri=uri)
        return role

    def safe_delete(self):
        "Delete object, but only if it not referenced by other objects."
        if len(self.statements) == 1:
            self.delete()

    def to_ipif(self):
        "Return role as IPIF-config dict."
        ipif_dict = {}
        if self.uri:
            ipif_dict["uri"] = self.uri
        if self.label:
            ipif_dict["label"] = self.label
        return ipif_dict


def define_entities(db):
    """Define all entities for db.

    This has to be in a function because database creation also
    happens in a function.
    """

    class Person(db.Entity, IPIFMixin):
        "A Person ORM entitiy."
        id = orm.PrimaryKey(str)
        createdBy = orm.Optional(str)
        createdWhen = orm.Optional(datetime.datetime)
        modifiedBy = orm.Optional(str)
        modifiedWhen = orm.Optional(datetime.datetime)
        uris = orm.Set("PersonURI")
        factoids = orm.Set("Factoid", cascade_delete=False)

        def update_from_ipif(self, ipifdata):
            """Update Person using `ipifdata`.

            `ipifdata` is a IPIF conform dict.
            """
            data = copy.deepcopy(ipifdata)
            # id must not be overwritten
            data.pop("@id", None)
            data.pop("id", None)
            # Delete and recreate all uris to avoid orphaned uris
            for uri in self.uris:
                uri.safe_delete()
                db.flush()
            data["uris"] = [
                PersonURI.get_for_update(uri=u) or PersonURI(uri=u) for u in data.get("uris", [])
            ]
            if data.get('createdWhen', ''):
                data['createdWhen'] = fix_datetime(data['createdWhen'])
            if data.get('modifiedWhen', ''):
                data['modifiedWhen'] = fix_datetime(data['modifiedWhen'])
            self.set(**data)

        def deep_delete(self):
            """Like delete() but also removes PersonURIs if orphaned.
            """
            for uri in self.uris:
                uri.safe_delete()
            if self.factoids == []:
                self.delete()

    class Source(db.Entity, IPIFMixin):
        "A Soure ORM entitiy."
        id = orm.PrimaryKey(str)
        createdBy = orm.Optional(str)
        createdWhen = orm.Optional(datetime.datetime)
        modifiedBy = orm.Optional(str)
        modifiedWhen = orm.Optional(datetime.datetime)
        label = orm.Optional(str)
        uris = orm.Set("SourceURI")
        factoids = orm.Set("Factoid", cascade_delete=False)

        def update_from_ipif(self, ipifdata):
            """Update Source using `ipifdata`.

            `ipifdata` is a IPIF conform dict.
            """
            data = copy.deepcopy(ipifdata)
            # id must not be overwritten
            data.pop("@id", None)
            data.pop("id", None)
            for uri in self.uris:
                uri.safe_delete()
                db.flush()
            data["uris"] = [
                SourceURI.get(uri=u) or SourceURI(uri=u) for u in data.get("uris", [])
            ]
            if data.get('createdWhen', ''):
                data['createdWhen'] = fix_datetime(data['createdWhen'])
            if data.get('modifiedWhen', ''):
                data['modifiedWhen'] = fix_datetime(data['modifiedWhen'])
            self.set(**data)

        def deep_delete(self):
            """Like delete but also removes orphaned SourceURIs.
            """
            for uri in self.uris:
                uri.safe_delete()
            if self.factoids == []:
                self.delete()

    class Statement(db.Entity, IPIFMixin):
        "A Statement ORM entitiy."

        id = orm.PrimaryKey(str)
        createdBy = orm.Optional(str)
        createdWhen = orm.Optional(datetime.datetime)
        modifiedBy = orm.Optional(str)
        modifiedWhen = orm.Optional(datetime.datetime)
        name = orm.Optional(str)
        date = orm.Optional("Date")
        role = orm.Optional("Role")
        statementContent = orm.Optional(str)
        statementType = orm.Optional("StatementType")
        memberOf = orm.Optional("MemberGroup")
        relatesToPersons = orm.Set("RelatesToPerson")
        places = orm.Set("Place")
        uris = orm.Set("StatementURI")
        factoid = orm.Optional("Factoid", cascade_delete=False)

        def update_from_ipif(self, ipifdata):
            """Update Statement using `ipifdata`.

            `ipifdata` is a IPIF conform dict.
            """
            data = copy.deepcopy(ipifdata)
            # id must not be overwritten
            data.pop("@id", None)
            data.pop("id", None)
            # handle related tables
            if self.date is not None:
                self.date.safe_delete()
            if "date" in data:
                data["date"] = Date.get_or_create(**data["date"])

            if self.role is not None:
                self.role.safe_delete()
            if "role" in data:
                data["role"] = Role.get_or_create(**data["role"])

            if self.memberOf is not None:
                self.memberOf.safe_delete()
            if "memberOf" in data:
                data["memberOf"] = MemberGroup.get_or_create(**data["memberOf"])

            if self.statementType is not None:
                self.statementType.safe_delete()
            if "statementType" in data:
                data["statementType"] = StatementType.get_or_create(
                    **data["statementType"]
                )

            # n:m
            for place in self.places:
                place.safe_delete()
            for rel_pers in self.relatesToPersons:
                rel_pers.safe_delete()
            for uri in self.uris:
                uri.safe_delete()
            db.flush()
            if "places" in data:
                data["places"] = [
                    Place.get_or_create(**place) for place in data["places"]
                ]
            if "relatesToPersons" in data:
                data["relatesToPersons"] = [
                    RelatesToPerson.get_or_create(**pers)
                    for pers in data["relatesToPersons"]
                ]
            if "uris" in data:
                data["uris"] = [
                    StatementURI.get(uri=u) or StatementURI(uri=u) for u in data["uris"]
                ]
            if data.get('createdWhen', ''):
                data['createdWhen'] = fix_datetime(data['createdWhen'])
            if data.get('modifiedWhen', ''):
                data['modifiedWhen'] = fix_datetime(data['modifiedWhen'])
            self.set(**data)

        def to_ipif(self):
            "Return a ORM object as IPIF-conform dictionary."

            data = self.to_dict()
            data["@id"] = data.pop("id")
            if data.get("createdWhen"):
                data["createdWhen"] = data["createdWhen"].isoformat()
            else:
                data["createdWhen"] = ""
            if data.get("modifiedWhen"):
                data["modifiedWhen"] = data["modifiedWhen"].isoformat()
            else:
                data["modifiedWhen"] = ""

            if self.date:
                data["date"] = self.date.to_ipif()
            if self.role:
                data["role"] = self.role.to_ipif()  ## mk_label_uri_dict(data.role)
            if self.memberOf:
                data[
                    "memberOf"
                ] = self.memberOf.to_ipif()  ## mk_label_uri_dict(data['memberOf'])
            if self.statementType:
                data[
                    "statementType"
                ] = (
                    self.statementType.to_ipif()
                )  ##mk_label_uri_dict(data['statementType'])
            data["uris"] = sorted([u.to_ipif() for u in self.uris])
            data["places"] = sorted(
                [p.to_ipif() for p in self.places], key=lambda x: x.get("label", "")
            )
            data["relatesToPersons"] = sorted(
                [rp.to_ipif() for rp in self.relatesToPersons],
                key=lambda x: x.get("label", ""),
            )
            data["factoid-refs"] =[]
            if self.factoid:
                data['factoid-refs'].append(self.factoid.get_refs())
            data["factoid-refs"].sort(key=lambda f: f['@id'])
            return data


        def deep_delete(self):
            """Like delete but also removes orphaned referenced entries from other tables.
            """
            if self.uris:
                for uri in self.uris:
                    uri.safe_delete()
            if self.relatesToPersons:
                for rel_pers in self.relatesToPersons:
                    rel_pers.safe_delete()
            if self.places:
                for place in self.places:
                    place.safe_delete()
            if self.date:
                self.date.safe_delete()
            if self.role:
                self.role.safe_delete()
            if self.statementType:
                self.statementType.safe_delete()
            if self.memberOf:
                self.memberOf.safe_delete()
            #if self.factoid is None:
            self.delete()

    class Factoid(db.Entity, IPIFMixin):
        "A Factoid ORM entitiy."
        id = orm.PrimaryKey(str)
        createdBy = orm.Required(str)
        createdWhen = orm.Required(datetime.datetime)
        modifiedBy = orm.Optional(str)
        modifiedWhen = orm.Optional(datetime.datetime)
        # Using a self reference to Factoid instead of str for derivedFrom does mot make
        # sense here, because everything we will ever need is the id of the other Factoid.
        derivedFrom = orm.Optional(str)
        person = orm.Required(Person)
        source = orm.Required(Source)
        statements = orm.Set(Statement)

        @classmethod
        def create_from_ipif(cls, ipif_data):
            "Create a factoid from a IPIF conform dictionary."
            data = copy.deepcopy(ipif_data)
            data["id"] = data.pop("@id") if "@id" in data else cls.make_id(data)

            data["person"] = Person.get(
                id=data["person"]["@id"]
            ) or Person.create_from_ipif(data["person"])
            data["source"] = Source.get(
                id=data["source"]["@id"]
            ) or Source.create_from_ipif(data["source"])
            data['statements'] = [Statement.create_from_ipif(s) for s in data['statements']]
            if data.get('createdWhen', ''):
                data['createdWhen'] = fix_datetime(data['createdWhen'])
            if data.get('modifiedWhen', ''):
                data['modifiedWhen'] = fix_datetime(data['modifiedWhen'])
            return cls(**data)

        def update_from_ipif(self, ipifdata):
            """Update Factoid from IPIF conform json-like dict.
            """
            data = copy.deepcopy(ipifdata)
            # id must not be overwritten
            data.pop("@id", None)
            data.pop("id", None)


            if self.person.id == data["person"]["@id"]:
                # Update data for existing person
                self.person.update_from_ipif(data.pop("person"))
            else:  # remove old person and a the new one
                self.person.deep_delete()
                # db.flush("places)
                self.person = Person.create_from_ipif(data.pop("person"))

            if self.source.id == data["source"]["@id"]:
                # Update data for existing source
                self.source.update_from_ipif(data.pop("source"))
            else:  # remove old source and a the new one
                self.source.deep_delete()
                self.source = Source.create_from_ipif(data.pop("source"))

            for stmt in self.statements:
                stmt.deep_delete()
            db.flush()
            for stmt in data.pop('statements'):
                self.statements.add(Statement.create_from_ipif(stmt))
            if data.get('createdWhen', ''):
                data['createdWhen'] = fix_datetime(data['createdWhen'])
            if data.get('modifiedWhen', ''):
                data['modifiedWhen'] = fix_datetime(data['modifiedWhen'])
            self.set(**data)

        def to_ipif(self):
            "Return a ORM object as IPIF-conform dictionary."
            data = self.to_dict()
            data["@id"] = data.pop("id")
            if data.get("createdWhen"):
                data["createdWhen"] = data["createdWhen"].isoformat()
            else:
                data["createdWhen"] = ""
            if data.get("modifiedWhen"):
                data["modifiedWhen"] = data["modifiedWhen"].isoformat()
            else:
                data["modifiedWhen"] = ""
            data["person"] = self.person.to_ipif()
            data["source"] = self.source.to_ipif()
            data['statements'] = []
            for stmt in self.statements:
                data["statements"].append(stmt.to_ipif())
            data["person-ref"] = {'@id': self.person.id}
            data["source-ref"] = {'@id': self.source.id}
            data["statement-refs"] = []
            for stmt in self.statements:
                data['statement-refs'].append({'@id': stmt.id})
            data['statement-refs'].sort(key=lambda s: s['@id'])
            return data

        def get_refs(self):
            """Return a factoid-refs dict."""
            refs = {}
            refs["@id"] = self.id
            refs['source-ref'] = {'@id': self.source.id}
            refs['person-ref'] = {'@id': self.person.id}
            refs['statement-refs'] = []
            for stmt in self.statements:
                refs['statement-refs'].append({'@id': stmt.id})
            refs['statement-refs'].sort(key=lambda s: s['@id'])
            return refs

        def deep_delete(self):
            """Like delete but also removes orphaned referenced entries from other tables.
            """
            p_id = self.person.id
            s_id = self.source.id
            stmt_ids = [stmt.id for stmt in self.statements]
            self.delete()

            person = Person[p_id]
            if person.factoids.count() == 0:
                person.deep_delete()

            source = Source[s_id]
            if source.factoids.count() == 0:
                source.deep_delete()

            for stmt_id in stmt_ids:
                statement = Statement[stmt_id]
                if statement.factoid is None:
                    statement.deep_delete()

    class Date(db.Entity):
        "A Date ORM entitiy as used in Statement."
        # we need an explicit id as all other fields are optional
        id = orm.PrimaryKey(int, auto=True)
        sortDate = orm.Optional(datetime.date)
        label = orm.Optional(str)
        statements = orm.Set(Statement)

        def safe_delete(self):
            "Delete object, but only if it not referenced by any other object."
            if len(self.statements) == 1:
                self.delete()

        @classmethod
        def get_or_create(cls, label="", sortDate=None):
            """Return a Date object with this combination of label and sortDate.
            If no such object exists, it will be created.
            """
            # IPIF allows '' as sortDate, but Pony wants a Date or None
            if sortDate is not None and sortDate == "":
                sortDate = None
            date = cls.get(label=label, sortDate=sortDate)
            if not date:
                date = cls(label=label, sortDate=sortDate)
            return date

        def to_ipif(self):
            "Return date as IPIF-config dict."
            ipif_dict = {}
            if self.sortDate:
                ipif_dict["sortDate"] = self.sortDate.isoformat()
            if self.label:
                ipif_dict["label"] = self.label
            return ipif_dict

    class Role(db.Entity, LabelUriMixin):
        "A Role ORM entitiy as used in Statement."
        # we need an explicit id as uri is optional
        id = orm.PrimaryKey(int, auto=True)
        label = orm.Optional(str)
        uri = orm.Optional(str)
        statements = orm.Set(Statement)

    class MemberGroup(db.Entity, LabelUriMixin):
        """A MemberGroup ORM entitiy as used in Statement.

        Defined als 'A group or organisation a person can be member of.'
        """

        # we need an explicit id as uri is optional
        id = orm.PrimaryKey(int, auto=True)
        label = orm.Optional(str)
        uri = orm.Optional(str)
        statements = orm.Set(Statement)

    class StatementType(db.Entity, LabelUriMixin):
        "A StatementType ORM entitiy as used in Statement."
        id = orm.PrimaryKey(int, auto=True)
        label = orm.Optional(str)
        uri = orm.Optional(str)
        statements = orm.Set(Statement)

    class Place(db.Entity, LabelUriMixin):
        "A Place ORM entitiy as used in Statement."
        # we need an explicit id as uri is optional
        id = orm.PrimaryKey(int, auto=True)
        uri = orm.Optional(str)
        label = orm.Optional(str)
        statements = orm.Set(Statement)

    class RelatesToPerson(db.Entity, LabelUriMixin):
        "A RelatesToPerson ORM entitiy as used in Statement."
        # we need an explicit id as uri is optional
        id = orm.PrimaryKey(int, auto=True)
        uri = orm.Optional(str)
        label = orm.Optional(str)
        statements = orm.Set(Statement)

    class PersonURI(db.Entity):
        """A PersonURI ORM entitiy as used in Person.

        A Person can have any number of uris.
        """

        uri = orm.PrimaryKey(str)
        persons = orm.Set(Person)

        def safe_delete(self):
            "Delete uri, but only if it is not referenced from any other person."
            if len(self.persons) == 1:
                self.delete()

        def to_ipif(self):
            "Return object in an IPIF-config way."
            return self.uri

    class SourceURI(db.Entity):
        """A SourceURI ORM entitiy as used in Source.

        A Source can have any number of uris.
        """

        uri = orm.PrimaryKey(str)
        sources = orm.Set(Source)

        def safe_delete(self):
            "Delete uri, but only if it is not referenced from any other source"
            if len(self.sources) == 1:
                self.delete()

        def to_ipif(self):
            "Return object in an IPIF-config way."
            return self.uri

    class StatementURI(db.Entity):
        """A StatementURI ORM entitiy as used in Statement.

        A Statement can have any number of uris.
        """

        uri = orm.PrimaryKey(str)
        statements = orm.Set(Statement)

        def safe_delete(self):
            "Delete uri, but only if it is not referenced from any other statement."
            if len(self.statements) == 1:
                self.delete()

        def to_ipif(self):
            "Return object in an IPIF-config way."
            return self.uri


def make_db(
    provider="sqlite", filename="", host="", port="", user="", password="", database=""
):
    "Return a Pony db object based on the parameters."
    db = orm.Database()
    if provider == "sqlite":
        if filename:
            db.bind(provider="sqlite", filename=filename, create_db=True)
        else:
            db.bind(provider="sqlite", filename=":memory:", create_db=True)
    else:
        db.bind(
            provider=provider,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
    define_entities(db)
    db.generate_mapping(create_tables=True)
    return db
