#!/bin/bash
# This script is to be run either manually or by the CI
# integration tool. It will run the containers before executing
# the testing suite

set -e

cd `dirname $0`

# Create the docker network
docker network create mudrchandler_test

# Run an instance of the virtuoso db
docker run -d --name=mudrchandler_test_db \
	--net mudrchandler_test \
	--network-alias database \
	-e SPARQL_UPDATE=true \
	-e DEFAULT_GRAPH=http://mu.semte.ch/test \
	-p 8890:8890 \
	tenforce/virtuoso:1.2.0-virtuoso7.2.2

# Run an instance of the delta service
docker run -d --name=mudrchandler_test_delta \
	--net mudrchandler_test \
	--network-alias delta \
	-e CONFIGFILE=/config/config.properties \
	-e SUBSCRIBERSFILE=/config/subscribers.json \
	-v "$PWD"/delta:/config \
	-p 8891:8890 \
	semtech/mu-delta-service:beta-0.9

docker pull bde2020/mu-docker-compose-handler:latest