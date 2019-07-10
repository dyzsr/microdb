#!/bin/sh

pip3 install tornado --user

cd ui && yarn && yarn build
