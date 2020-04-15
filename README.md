# GraphSense TagPacks

A TagPack is a collection of cryptoasset attribution tags with associated
provenance and categorization metadata. This repository provides

* a common structure (schema) for TagPacks
* a tool for validating and ingesting TagPacks into [Apache Cassandra][cassandra]
* a curated Git infrastructure for collaboratively collecting TagPacks from public sources

## TagPack

### What is an attribution tag?

An attribution tag is any form of context information that can be attributed to
a cryptoasset address. The following example attributes a Bitcoin address to
the Internet Archive, which is, according to
[this source](https://archive.org/donate/cryptocurrency/), the holder of that
address:

    label: Internet Archive
    address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
    source: https://archive.org/donate/cryptocurrency/

### Why are attribution tags important?

Cryptoasset analytics relies on two complementary techniques: **address
clustering**, which relies on heuristics to group multiple addresses into
maximal subsets that can likely be assigned to the same real-world actor, and
**attribution tags** as shown above. The strength lies in the combination of
these techniques: a tag attributed to a single address belonging to a larger
cluster can easily add contextual information to hundreds of thousands
cryptocurrency addresses.

**Note**: certain types of transactions (e.g., CoinJoins, Mixing Services) can
distort clustering results and lead to false, unreliable, or intentionally
misplaced attribution tags that could associate unrelated actors with a given
cluster.

### How does a TagPack look like?

A TagPack defines a structure for collecting and packaging attribution tags
with additional provenance metadata (e.g., title, creator, etc.).

TagPacks are represented as [YAML][yaml] files, which can easily
be created by hand or exported automatically from other systems.

Here is a minimal TagPack example with mandatory properties:

    ---
    title: First TagPack Example
    creator: John Doe
    tags:
        - label: Internet Archive
          address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
          source: https://archive.org/donate/cryptocurrency/
          lastmod: 2019-03-15
          currency: BTC
        - label: Example
          address: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
          source: https://example.com
          lastmod: 2019-03-15
          currency: BTC

TagPacks can be shared via some Git-Service (Github in this case), which enables
version control and fine-grained recording of modifications.

#### TagPack properties

A TagPack defines a **header** with a number of mandatory and optional fields and a
**body** containing a list of tags. In the above example, `title` and `creator` are
part of the TagPack header, the list of `tags` represent the body.

Please note that allowed properties are defined in the TagPack schema, which defines
**mandatory** and **optional** fields for the TagPack header and body. In the above
example, `label`, `address`, and `source` are mandatory properties as they
describes where a certain piece of information is coming from (either in the form
of a URI or a textual description).

The range of defined properties is defined in `TODO: point to location` and looks
like this:

    header:
      - title
      - creator
      - description
      - tags
    body:
      - tag:
          - address
          - label
          - source
          - currency
          - category
          - lastmod
          - abuse

#### Property inheritance

In the above example, the same `lastmod` and `currency` property values are repeated
for both tags, which represents an unnecessary repetition of the same information.

To avoid this, body fields can also be added to the header and then apply to all
tags in the body. Thus, they are *abstracted* into the header and then inherited by all
body elements, as shown in the following example.

    ---
    title: Second TagPack Example
    creator: John Doe
    lastmod: 2019-03-15
    currency: BTC
    tags:
        - label: Internet Archive
          address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
          source: https://archive.org/donate/cryptocurrency/
        - label: Example
          address: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
          source: https://example.com

#### Property override

It is also possible to override abstracted fields in the body. This could be relevant if
someone creates a TagPacks comprising several tags and then adds additional tags later
on, which then, of course, have different `lastmod` property values.

The following example shows several tags associating addresses from various
cryptocurrencies with the label `Internet Archive`. Most of them were collected
at the same time (2019-03-15), except the Zcash tag that has been collected
and added later (2019-03-20).


    ---
    title: Third TagPack Example
    creator: John Doe
    description: A collection of tags commonly used for demonstrating GraphSense features
    lastmod: 2019-03-15
    label: Internet Archive
    source: https://archive.org/donate/cryptocurrency
    category: Organization
    tags:
        - address: 1Archive1n2C579dMsAu3iC6tWzuQJz8dN
          currency: BTC
        - address: 1K1rgZ1dz9w7dsR1HGS1drmzfUHMtqx1Tc
          currency: BCH
        - address: "0xFA8E3920daF271daB92Be9B87d9998DDd94FEF08"
          currency: ETH
        - address: rGeyCsqc6vKXuyTGF39WJxmTRemoV3c97h
          currency: XRP
        - address: t1ZmpK4QFcvyQZ3ghTgSboBW8b4HgiZHQF9
          currency: ZEC
          lastmod: 2019-04-16


#### Identification and Uniqueness of TagPacks and Tags

TagPacks are uniquely identified by a URI.

Since TagPacks are essentially files pushed to some Git repository, they can be
uniquely identified by their Git URI
(e.g., `https://github.com/graphsense/graphsense-tagpacks/blob/master/packs/demo.yaml`).

Within a TagPack, tags are treated as **first-class objects** that are identified by
the combination the mandatory body fields `address`, `label`, `source`.

That implies that the same label (e.g., `Internet Archive`) can be assigned several
times to the same address (e.g., `1Archive1n2C579dMsAu3iC6tWzuQJz8dN`),
typically by different parties.

#### Using Concepts from Public Taxonomies

The use of a common terminology is essential for data sharing and establishing interoperability
across tools. Therefore, the TagPack schema defines two properties that take concepts from
agreed upon taxonomies as values:

* `category`: defines the type of real-world entity that is control of a given address. Possible
concepts (e.g., Exchange, Marketplace) are defined in the
[INTERPOL Darkweb and Cryptoassets Entity Taxonomy][dn-ca].

* `abuse`: if an address was involved in some abusive behavior, this property's value defines the
type of abuse and can take values from the [INTERPOL Darkweb and Cryptoassets Abuse Taxonomy][dn-ca].

## tagpack Tool

The tagpack provides utility functions for validating and ingesting TagPacks
into an [Apache Cassandra database][cassandra], which is required before running
the [graphsense-transformation](https://github.com/graphsense/graphsense-transformation)
pipeline.

It is made available as a Python package.

### Install from Remote

    pip install tagpack

### Local Development Setup

Create and activate a python environment for required dependencies

    python3 -m venv venv
    . venv/bin/activate

Install project and required dependencies in local environment

    pip install -e .

### Configure a TagPack Repository

The tagpack is typically executed from within a folder (a repository) containing
TagPack files - a so called **TagPack Repository**.

Before commands can be executed, a file `config.yaml` must be present in the path where
the tool is executed. It must define the `baseURI` (e.g., the Git URI) of this TagPack
Repository as well as pointers to the taxonomies to be used with this repository.

    baseURI: https://github.com/graphsense/graphsense-tagpacks
    taxonomies:
      entity: https://interpol-innovation-centre.github.io/DW-CC-Taxonomy/assets/data/entities.csv
      abuse: https://interpol-innovation-centre.github.io/DW-CC-Taxonomy/assets/data/abuses.csv

### Handle Referenced Taxonomies (by example)

List configured taxonomy keys and URIs

    tagpack taxonomy

Fetch and show concepts of a specific remote taxonomy (referenced by key)

    tagpack taxonomy abuse show

Ingest concepts from a remote taxonomy into GraphSense

    cqlsh localhost -f cql/tagpack_schema.cql
    tagpack taxonomy abuse ingest

### Validate a TagPack

Validate a single TagPack file

    tagpack validate <file>

Recursively validate all TagPacks in (a) given folder(s).

    tagpack validate -r <root_folder1> [<root_folder2> ...]

## Ingest a TagPack into a local

Create a `tagpacks` schema in your local Cassandra instance

    tagpack create-keyspace -h <cassandra_host> [-k <keyspace>]

Ingest a single TagPack

    tagpack ingest -h <cassandra_host> [-k <keyspace>] <tagPack_file>

Ingest all TagPacks in (a) given folder(s).

    tagpack ingest -h <cassandra_host> [-k <keyspace>] [-r] <root_folder1> [<root_folder2> ...]

Optionally, you can specific the batch size for tuning ingest performance.

    tagpack ingest -h <cassandra_host> [-k <keyspace>] [-b <batch_size>] [-r] <root_folder1> [<root_folder2> ...]
    

## Collaborative Collection and Sharing TagPacks

This repository also provides a curated collection of TagPacks, which have been
collected from **public sources** either by the GraphSense team or from other
contributors.

All TagPacks in this repository must fulfill the following criteria:

1.) None of the tags contains personally identifiable information (PII)

2.) All tags originate from public sources

3.) All tags provide a dereferenceable pointer (link) to their origin

If someone wants to create TagPacks not fulfilling these criteria, it is of course
possible to store them privately, e.g., on the local filesystem or a local
Git instance.

### How can I contribute TagPacks to this repository?

**Step 1**: [Fork](https://help.github.com/en/articles/fork-a-repo) this repository

**Step 2**: Add your TagPacks to the folder `packs`

**Step 3**: Validate your TagPack

**Step 4**: Contribute them to GraphSense public TagPack collection by submitting a [pull request](https://help.github.com/en/articles/about-pull-requests)


[cassandra]: https://cassandra.apache.org/
[yaml]: [https://yaml.org/]
[dn-ca]: https://interpol-innovation-centre.github.io/DW-CC-Taxonomy/


