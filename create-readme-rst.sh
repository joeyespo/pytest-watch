#!/bin/sh

set -u

ROOTPATH=$(dirname $0)

VIRTUALENV_ROOT=/tmp/venv/
VIRTUALENV_BIN=${VIRTUALENV_ROOT}bin/
VIRTUALENV_PIP=${VIRTUALENV_BIN}/pip

virtualenv "$VIRTUALENV_ROOT"

$VIRTUALENV_PIP install --upgrade pandoc
pandoc -t rst -o "$ROOTPATH/README.rst" "$ROOTPATH/README.md"

set +u
