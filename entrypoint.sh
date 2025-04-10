#!/bin/bash
set -e

echo "🔧 Entrypoint starting with JOB_NAME=$JOB_NAME and SCHEDULE=$SCHEDULE"

python /app/main.py
