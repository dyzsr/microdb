#!/bin/sh

export PYTHONPATH="./"
nohup python3 web/run.py &
cd ui && yarn run serve -s build
