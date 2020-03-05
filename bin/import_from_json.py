import click
import json
import re
import requests
import logging
import urllib.parse

#def clean_id(id_):
#    return id_

def post(url, data):
    "A post request with some error handling."
    r = requests.post(url, json=data)
    if r.status_code > 210:
        raise Exception(r.text)
    return r.json


def put(url, data):
    "A put request with some error handling."
    r = requests.put(url, json=data)
    if r.status_code > 210:
        raise Exception(r.text)
    return r.json

def insert_person(data, baseurl):
    if data["@id"]:
        url = "{}/persons/{}".format(baseurl, data['@id'])
        person = put(url, data)
    else:
        url = "{}/persons".format(baseurl)
        person = post(url, data)
    return person

def insert_source(data, baseurl):
    if data["@id"]:
        url = "{}/sources/{}".format(baseurl, data['@id'])
        source = put(url, data)
    else:
        url = "{}/sources".format(baseurl)
        source = post(url, data)
    return source

def insert_factoid(data, baseurl):
    if data["@id"]:
        url = "{}/factoids/{}".format(baseurl, data['@id'])
        factoid = put(url, data)
    else:
        url = "{}/factoids".format(baseurl)
        factoid = post(url, data)
    return factoid


def set_log_level(verbosity):
    vlen = len(verbosity)
    if vlen == 0:
        logging.basicConfig(level=logging.WARNING)
    elif vlen == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)


def is_valid_id(id_):
    """Test if on allowed chars are in id.
    
    These chars are: [A-Za-z0-9_.\\-~]
    See RFC3986#section-2.3
    # Possibly extend to IRI?
    """
    if not re.match(r'^[%A-Za-z0-9_.\\\-~]*$', id_):
        return False
    return True

def check_ids(factoids):
    "Return True if all ids in factoid are RFC 3986 conform."
    is_conform = True
    for factoid in factoids:
        if not is_valid_id(factoid['@id']):
            print("Factoid id '{}' does not conform to RFC 3986#section-2.3".format(factoid['@id']))
            is_conform = False
        if not is_valid_id(factoid['person']['@id']):
            print("Person id '{}' in Factoid '{}' does not conform to RFC 3986#section-2.3".format(factoid['person']['@id'], factoid['@id']))
            is_conform = False
        if not is_valid_id(factoid['source']['@id']):
            print("Source id '{}' in Factoid '{}' does not conform to RFC 3986#section-2.3".format(factoid['source']['@id'], factoid['@id']))
            is_conform = False
        if not is_valid_id(factoid['statement']['@id']):
            print("Statement id '{}' in Factoid '{}' does not conform to RFC 3986#section-2.3".format(factoid['statement']['@id'], factoid['@id']))
            is_conform = False
    return is_conform

def import_factoids(data, baseurl,auto_escape=False):
    inserted_f_ids = []
    try:
        for i, factoid in enumerate(data["factoids"]):
            logging.info('Processing factoid {}/{}'.format(i, len(data["factoids"])))
            person = factoid.pop('person')
            if auto_escape:
                person['@id'] = urllib.parse.quote(person['@id'])
            insert_person(person, baseurl)
            
            source = factoid.pop('source')
            if auto_escape:
                source['@id'] = urllib.parse.quote(source['@id'])
            insert_source(source, baseurl)

            if auto_escape:
                factoid['@id'] = urllib.parse.quote(factoid['@id'])
            factoid['person'] = {'@id': person['@id']}
            factoid['source'] = {'@id': source['@id']}
            factoid = insert_factoid(factoid, baseurl)
            #inserted_f_ids.append(factoid['@id'])
            # TODO: to a rollback???

    except Exception as err:
        # for p_id in p_ids:
        #     requests.delete(baseurl + '/persons/' + p_id)
        #     # fixme: zuerst die faktoide löschen, dann die anderen ggf, 409 abfangen 
        #     # und ame ende noch einmalprobieren.
        raise err



@click.command()
@click.argument("jsonfile")
@click.option("-s", "--scheme", default="https", help="Scheme to use. Defaults to https")
@click.option("-H", "--host", default="localhost", help="Hostname of the server")
@click.option("-p", "--port", type=int, default=5000, help="Port of the server")
@click.option("-b", "--base-path", default="/api", help="Base path to PAPI service on host")
@click.option("-v", "--verbosity", is_flag=True, multiple=True, help="Increase verbosity")
@click.option("-e", "--auto-escape-ids", is_flag=True, default=False, help="Automatically escape invald characters in '@id' values")
def main(jsonfile, scheme, host, port, base_path, verbosity, auto_escape_ids):
    set_log_level(verbosity)
    baseurl = '{}://{}:{}{}'.format(scheme, host, port, base_path)
    logging.info("Using '{}' as baseurl".format(baseurl))
    logging.debug("Reading file: '{}'".format(jsonfile))
    with open(jsonfile) as fh:
        data = json.load(fh)

    if auto_escape_ids:
        import_factoids(data, baseurl, True)
    else:
        if check_ids(data['factoids']):
            import_factoids(data, baseurl)
        else:
            print(('Found at least one problematic \'@id\' value. \n'
                   'Fix it manually or use the --auto-escape-ids option, which will escape '
                    'the problematic id but will result in ugly urls.'))



if __name__ == '__main__':
    main()
