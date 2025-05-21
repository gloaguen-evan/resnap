#!/bin/bash

set -e

docker build -f Dockerfile_tests -t test_lib .
docker run --rm -it --name test_lib test_lib