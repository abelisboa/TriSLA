#!/bin/bash
set -e

FRONTEND_DIR="$(pwd)/trisla-portal/frontend"
IMAGE="ghcr.io/abelisboa/trisla-portal-frontend:latest"

docker build -t $IMAGE $FRONTEND_DIR
docker push $IMAGE
