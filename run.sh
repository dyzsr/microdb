#!/bin/sh

nohup python3 web/run.py &
cd ui && yarn start
