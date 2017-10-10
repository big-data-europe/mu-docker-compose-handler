#!/bin/bash

# Run the set of tests. The tox tool will read the tox.ini
# file and that one will see all the virtualenv contexts
# specified and run the specific set of actions per each one.

set -e

cd `dirname $0`
cd ..

if [ -z "$1" ]; then
	commands=(tox)
else
	commands=("$@")
fi

exec docker run -it --rm \
	--net mudrchandler_test \
    --net-alias drc-handler \
	-e TOX=true \
	-e MU_APPLICATION_GRAPH=http://mu.semte.ch/test \
	-e MU_SPARQL_ENDPOINT=http://delta:8890/sparql \
	-v $PWD:/src \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-l com.docker.compose.project=APPDRCHANDLER \
	bde2020/mu-docker-compose-handler:latest "${commands[@]}"