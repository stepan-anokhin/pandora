# PANDORA

This small box of pandora (aka small app basis) composed from the following technologies:

* [Dgraph](https://dgraph.io/) as data store with GraphQL support, write operations using REST
* [Minio](https://www.minio.io/) as Amazon S3 compatible storage
* [Stow](https://github.com/graymeta/stow) allows using cloud storage provides like Amazon, Google, Azure
* [ElasticSearch](https://www.elastic.co/products/elasticsearch) as search engine. Dgraph data can be automatically replicated in ElasticSeach index
* [Kibana](https://www.elastic.co/products/kibana) to explore ElasticSearch data
* [NATS](https://nats.io/) as messaging system with streaming of push notifications (events) via [SSE](https://en.wikipedia.org/wiki/Server-sent_events) channel
* [Celery](http://www.celeryproject.org/) - distributed task queue
* [RabbitMQ](https://www.rabbitmq.com/) - fast message broker for celery tasks
* [Redis](https://redis.io/) - result backend for celery tasks and cache service
* [Apache Tika](https://tika.apache.org/) - powerful content analysis toolkit
* try [FluentD](https://www.fluentd.org/) - for centralized logging, not implemented yet :)

Programming languages currently used in the project:
* [Go](https://golang.org/)
* [Python](https://www.python.org/)
* [Kotlin](https://kotlinlang.org/)

## Basic Idea

I'd like to have simple, flexible, dynamic, declarative, reactive, realtime information system :)

## How to run

`docker-compose up` runs the following services:

1. `zero` - Dgraph cluster manager
1. `dgraph` - Dgraph data manager hosts predicates & indexes
1. `ratel` - serves the UI to run queries, mutations & altering schema
1. `nats` - plays as message bus
1. `pubsub` - event streaming service based on [SSE](https://en.wikipedia.org/wiki/Server-sent_events) protocol
1. `minio` - Amazon S3 compatible file store
1. `imageproxy` - [service](https://willnorris.com/go/imageproxy) with image manipulation ops like resizing
1. `elasticsearch` - search and analitycs engine
1. `kibana` - Elasticsearch dashboard
1. `app` - application API service
1. `caddy` - web server as service gateway

## How to build

To start developing a project, you need to
install git:

    $ sudo apt-get install git

For the `add-apt-repository` to work install package:

    $ sudo apt install software-properties-common

software-properties-common - This software provides an abstraction of the used apt repositories. This allows you to easily manage your distribution and independent software vendors.

Install Docker following [these instructions](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

Add repository to install Go:

    $ sudo add-apt-repository ppa:longsleep/golang-backports

Install Go:

    $ sudo apt-get update
    $ sudo apt-get install golang-go

Run docker services:

    $ docker-compose up 

Run the script initdata.py (fill the database) execute commands:

    $ apt install python-pip
    $ pip install pipenv
    $ pipenv install
    $ pipenv shell

Then execute the script itself:

    $ python initdata.py

## How to run tests

* `go test -coverprofile cover.out`
* `go tool cover -html cover.out`
