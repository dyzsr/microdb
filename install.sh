#!/bin/sh

pip3 install tornado --user

cd ui
npm install
npm run build
