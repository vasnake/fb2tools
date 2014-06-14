#!/usr/bin/env bash
# -*- mode: shell; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

PROJECT_DIR="/home/valik/data/projects/fb2tools"

main() {
    #~ createVirtualenv
    #~ makeSourceDistribution
    #~ installDevelop
    #~ createRequirements
    execFb2Tools
}

execFb2Tools() {
    pushd "${PROJECT_DIR}"
    source env/bin/activate
    export PYTHONIOENCODING=UTF-8
    python -u -m fb2tools namezip --workdir /home/valik/t/b2/zip --scandir /home/valik/t/b2/fb2
    python -u -m fb2tools stripauthor --workdir /home/valik/t/b2/zip
}

################################################################################

createVirtualenv() {
    pushd "${PROJECT_DIR}"
    virtualenv env
}

makeSourceDistribution() {
    pushd "${PROJECT_DIR}"
    source env/bin/activate
    python setup.py sdist
}

installDevelop() {
    pushd "${PROJECT_DIR}"
    source env/bin/activate
    python setup.py develop
}

createRequirements() {
    pushd "${PROJECT_DIR}"
    source env/bin/activate
    pip freeze > requirements.txt
    cat requirements.txt
}

main
