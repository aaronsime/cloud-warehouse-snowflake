#!/bin/bash
set -e

echo "🔧 Entrypoint starting with JOB_NAME=$JOB_NAME and SCHEDULE=$SCHEDULE"

if [[ "$JOB_NAME" == "snowflake_ingestion" ]]; then
  python /app/scheduler/jobs/snowflake_ingestion/main.py
elif [[ "$JOB_NAME" == "refresh_facts" || "$JOB_NAME" == "refresh_staging" || "$JOB_NAME" == "refresh_dimensions" || "$JOB_NAME" == "refresh_intermediate" ]]; then
  python /app/scheduler/jobs/transform_dbt/main.py
else
  echo "❌ Unknown job: $JOB_NAME"
  exit 1
fi
