#!/bin/bash

set -e

echo "Validating code..."

echo ""
echo "#########################################"
echo "### Validate imports order with Isort ###"
echo "#########################################"
isort .

echo ""
echo "#######################################"
echo "### Validate code style with Flake8 ###"
echo "#######################################"
flake8 .

echo ""
echo "#######################################"
echo "### Validate code style with Ruff ###"
echo "#######################################"
ruff check

echo ""
echo "##############################################"
echo "### Running tests and coverage with Pytest ###"
echo "##############################################"
pytest --cov=resnap --cov-report=html --cov-fail-under=100
