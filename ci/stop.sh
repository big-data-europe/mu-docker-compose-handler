#!/bin/bash
# Teardown all the previously booted testing
# containers

docker rm -vf mudrchandler_test_db
docker rm -vf mudrchandler_test_delta
docker network rm mudrchandler_test