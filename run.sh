#!/bin/sh

export PYTHONPATH="./"
nohup python3 web/run.py &
cd ui && npx serve -s build
