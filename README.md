# Cloud Warehouse Snowflake

## 🚀 Overview

This project provides a modular and scalable way to orchestrate data transformation jobs (e.g., dbt models or data ingestion tasks) using **Google Cloud Run**, **Cloud Scheduler**, **Pub/Sub**, and **Cloud Functions**.

It allows scheduled execution of multiple Cloud Run jobs defined in a `settings.yaml` file, all managed via infrastructure-as-code (Terraform), with logs routed to Cloud Logging.

---

## 📦 Architecture

```
Cloud Scheduler
     ↓
Pub/Sub (schedule topic)
     ↓
Cloud Function (Triggered)
     ↓
Reads `settings.yaml`
     ↓
Starts multiple Cloud Run jobs with appropriate ENV vars (e.g., JOB_NAME)
```

---

## 💠 Components

### 📟 1. `settings.yaml`
Defines job schedules and mappings:

```yaml
schedules:
  daily:
    - name: job_name
      run_job_name: job-name-example
      region: us-central1
      model: model_name (for dbt overrides)
```

### 💡 2. Cloud Function
Triggered by a Pub/Sub message, it:
- Parses the `settings.yaml` file
- Starts one or more Cloud Run jobs via the GCP Run API
- Logs details of the run

### 📼 3. Cloud Run Jobs
Each job container runs a specific data processing task, e.g., a dbt model execution. These jobs are built from a shared codebase and defined with Docker.

### ⏰ 4. Cloud Scheduler
Triggers the Pub/Sub topic on a schedule (e.g., every 6 hours, daily, etc.).

---

## 💡 Key Features

- ✅ YAML-driven job configuration
- ✅ Easily extendable to new jobs or schedules
- ✅ Uses native GCP services (no Airflow dependency)
- ✅ Logs all activity to Cloud Logging
- ✅ Jobs are fully containerized

---

## 💢 Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run Cloud Function locally:
```bash
functions-framework --target=subscribe
```

3. Trigger function:
```bash
curl -X POST http://localhost:8080/ -H "Content-Type: application/json" \
  -d '{"message": {"data": "<base64-encoded-schedule-payload>"}}'
```

---

## ⚙️ Environment Variables

The following are expected for the function and Cloud Run jobs:

| Variable         | Description                       |
|------------------|-----------------------------------|
| `PROJECT_ID`     | GCP project ID                    |
| `ENV`            | Environment (e.g., dev, prod)     |
| `REGION`         | Default region for Cloud Run jobs |

---

## 📜 Useful Terraform Modules

- Cloud Run job definitions
- IAM permissions
- Cloud Scheduler setup
- Cloud Function with trigger and permissions

---

## ✨ Example Use Case

You're running a data pipeline where multiple dbt transformation jobs must be triggered daily. Instead of managing them manually or using Airflow, this setup automates it using GCP native tooling and YAML configuration.

---

## 🧹 Future Enhancements

- Job failure alerting (via Slack or Error Reporting)
- Retry policies and dead-letter queues
- Job chaining via Cloud Workflows

---

## Testing

```
{
    "run_job_name": "cloud-scheduler-cloudrun-job-example",
    "region": "us-central1",
    "overrides": {
        "JOB_NAME": "job_example"
    }
}
```

## 🧑‍💻 Author
Built by [Aaron] 💡
