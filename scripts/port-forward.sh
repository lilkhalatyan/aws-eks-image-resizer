#!/usr/bin/env bash
set -euo pipefail
kubectl port-forward deploy/api 8080:8080