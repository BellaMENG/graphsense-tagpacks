"""Taxonomy - A proxy for a remote taxonomy defintion"""

import csv
from io import StringIO
import requests


class Concept(object):
    """Concept Definition.

    This class represents serves as a proxy for a concept that is defined
    in some remote taxonomy. It just provides the most essential properties.

    A concept can be viewed as an idea or notion; a unit of thought.
    See: https://www.w3.org/TR/skos-reference/#concepts

    """

    def __init__(self, id, uri, label, description):
        self.id = id
        self.uri = uri
        self.label = label
        self.description = description

    def __str__(self):
        s = [str(self.id), str(self.uri), str(self.label),
             str(self.description)]
        return "[" + " | ".join(s) + "]"


class Taxonomy(object):
    """TagPack Taxonomy Proxy.

    This class serves as a proxy for remote taxonomies defined at
    https://interpol-innovation-centre.github.io/DW-CC-Taxonomy/.

    It can be used for loading and parsing a taxonomy from remote
    and for ingesting a taxonomy into a local Cassandra data store.
    """

    def __init__(self, key, uri):
        self.key = key
        self.uri = uri
        self.concepts = []

    def load_from_remote(self):
        print("Loading taxonomy {} from {}".format(self.key, self.uri))
        response = requests.get(self.uri)
        f = StringIO(response.text)
        csv_reader = csv.DictReader(f, delimiter=',')
        for row in csv_reader:
            concept = Concept(row['id'], row['uri'],
                              row['label'], row['description'])
            self.concepts.append(concept)
