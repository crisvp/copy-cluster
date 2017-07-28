# Copy Elasticsearch Cluster

This is a small Python3 utility to copy indexes, mappings, and settings from one ElasticSearch cluster to another.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Python 3, Requests, optionally virtualenv and pip.

### Installing

Clone the repository.

```
git clone https://github.com/crisvp/copy-cluster.git
```

Set up a virtualenv:

```
virtualenv -p python3 env
source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```

Verify she chooches:

```
./copy-cluster.py -h
```

## Usage

### Description

This will copy indexes, aliases, and settings from one cluster to another. Data is **not** copied. For that, use a tool like [logstash](https://www.elastic.co/products/logstash) or [elasticsearch-reindex](https://github.com/garbin/elasticsearch-reindex).

The destination cluster should be completely empty so that indexes and aliases can be created. The tool is fairly basic. Any errors are passed on as exceptions, the tool will crash, and you will have to manually bring the destination cluster back into an empty state. Typically this just means deleting the indexes.

### Invocation

This will copy all indexes, settings, and aliases from the cluster at localhost:9200 to the cluster at localhost:9201:

```
./copy-cluster.py http://localhost:9200 http://localhost:9201
```

## Author

* **Cris van Pelt** - *Initial work* - [crisvp](https://github.com/crisvp)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
