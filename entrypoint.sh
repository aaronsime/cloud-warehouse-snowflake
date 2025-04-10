#!/bin/bash
set -e

if [[ "$JOB_NAME" == "snowflake_ingestion" ]]; then
  python /app/scheduler/jobs/snowflake_ingestion/main.py
elif [[ "$JOB_NAME" == "transform_dbt" ]]; then
  python /app/scheduler/jobs/transform_dbt/main.py  # ← your dbt runner
else
  echo "Unknown job: $JOB_NAME"
  exit 1
fi
