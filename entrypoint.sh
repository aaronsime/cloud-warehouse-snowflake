#!/usr/bin/env bash

# Exit on error, undefined variable, or failed command in pipeline
set -euo pipefail

job_name="$JOB_NAME"

echo "Starting job: $job_name"

# Execute main.py (should be located in project root)
python main.py
