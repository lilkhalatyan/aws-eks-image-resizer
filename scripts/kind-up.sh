#!/usr/bin/env bash
set -euo pipefail


# Create kind cluster if not exists
if ! kind get clusters | grep -q "image-resizer"; then
kind create cluster --name image-resizer --wait 120s
else
echo "kind cluster 'image-resizer' already exists"
fi


# Install/upgrade Helm release into default namespace
helm upgrade --install image-resizer deploy/charts/image-resizer \
--namespace default \
--create-namespace \
-f deploy/charts/image-resizer/values-local.yaml


echo "\n==> Next: port-forward API and test\n"