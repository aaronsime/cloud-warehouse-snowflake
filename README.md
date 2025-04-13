# 🧱 Cloud Warehouse Snowflake

![High Level Architecture](./high_level_architecture.png)

## 🚀 Overview

This project provides a modular, scalable, and cloud-native orchestration framework for managing data transformation jobs (e.g., dbt model execution) using **Google Cloud Run**, **Cloud Scheduler**, **Pub/Sub**, and **Cloud Functions**.

It enables:
- Configuration-driven scheduling via `settings.yaml`
- Dependency-aware execution (`depends_on` logic)
- Fully containerized job processing
- Native GCP integration (no Airflow)

---

## 📦 Architecture

```
Cloud Scheduler
     ↓
Pub/Sub (schedule topic)
     ↓
Cloud Function (triggered)
     ↓
Reads `settings.yaml` for the given schedule
     ↓
Resolves job dependencies
     ↓
Starts Cloud Run jobs in correct execution order
```

---

## 💠 Key Components

### ✅ `settings.yaml`

Defines jobs grouped by schedule with optional dependencies:

```yaml
schedules:
  daily:
    - name: refresh_staging
      run_job_name: dbt-transform-job
      region: australia-southeast1
      config:
        DBT_COMMAND: run
        DBT_MODELS: tag:staging
        DBT_TARGET: dev

    - name: refresh_facts
      depends_on: refresh_staging
      run_job_name: dbt-transform-job
      region: australia-southeast1
      config:
        DBT_COMMAND: run
        DBT_MODELS: tag:facts
        DBT_TARGET: dev
```

---

### 🧠 Dependency Resolver

Located in `utils/job_scheduler.py`, this Python-based resolver:
- Accepts a list of jobs with optional `depends_on`
- Recursively orders them via topological sort
- Prevents re-visiting shared dependencies
- Ensures correct execution order

---

### 🐍 Cloud Run Job Runner

Located in `scheduler/jobs/transform_dbt/main.py`, this script:
- Loads environment variables (`JOB_NAME`, `SCHEDULE`)
- Parses `settings.yaml`
- Resolves dependencies
- Runs dbt with mapped config

---

### ☁️ GCP Orchestration Layer

- **Cloud Scheduler**: Triggers job runs based on a cron schedule
- **Pub/Sub**: Delivers the schedule to a Cloud Function
- **Cloud Function**: Reads `settings.yaml`, resolves jobs, starts Cloud Run jobs
- **Cloud Run**: Executes dbt commands inside a containerized job

---

## ✅ Features

- 📄 YAML-driven job configuration
- 🔗 Native dependency resolution (`depends_on`)
- 🌐 GCP-native (no Airflow required)
- 🔧 Easily extensible
- 📦 Fully containerized with Docker
- 🪵 Logs integrated with Cloud Logging

---

## 🧪 Local Development

### 1. Load `.env` variables (PowerShell)

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match "^\s*([^#][^=]+?)\s*=\s*(.*)\s*$") {
    $key, $val = $matches[1], $matches[2]
    [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
  }
}
```

If testing changes to transform_dbt hardcode inside `main.py`:

```python

os.environ["JOB_NAME"] = "refresh_facts"
os.environ["SCHEDULE"] = "daily"

```

---

### 2. Run job locally

```bash
python scheduler/jobs/transform_dbt/main.py
```

This will:
- Load the job config from `settings.yaml`
- Resolve all dependencies
- Execute the ordered dbt commands


---

## 🛠 Terraform Modules

Includes infrastructure-as-code to provision:

- Snowflake warehouse
- Snowflake roles and privileges
- Snowflake users
- Snowflake database and schema
- gcp resources are maintained here: https://github.com/aaronsime/cloud-platform-gcp-tf

---

## 📊 Example Use Case

You're running multiple dbt model groups daily, and some models must run only after staging completes. Instead of managing this manually or using Airflow, this project enables:

- Centralized config in `settings.yaml`
- Dependency-aware execution
- Auto-triggered via Cloud Scheduler
- Containerized job execution via Cloud Run

---

## 🔮 Future Enhancements

- 🛎 Slack alerts for job failures/success
- 🔁 Retry policies and DLQ support
- 🔗 Job chaining with Cloud Workflows

---

## 👤 Author

Built by **Aaron Sime** — designed for teams looking to simplify data orchestration with clean, cloud-native tooling.
