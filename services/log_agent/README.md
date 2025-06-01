# AI-Powered Log Agent Service

A production-grade error monitoring system for DBT and Orchestration that automatically detects, analyzes, and alerts on DBT errors using AI-powered summaries.

## What it does

- **Monitors** DBT logs in real-time via Google Cloud Logging
- **Parses** 20+ types of DBT errors with structured extraction
- **Summarizes** errors using Gemini AI for different personas (engineers, analysts, data scientists)
- **Alerts** relevant teams via Slack with contextualized summaries
- **Stores** all errors and summaries in BigQuery for analysis

## Architecture

```
Cloud Logging → Pub/Sub → Cloud Run Job → Parser → Gemini AI → Slack
                                                            ↓
                                                       BigQuery
```

## Folder Structure

```
services/log_agent/
├── clients/
│   └── llm_client.py              # Gemini AI integration with multi-role analysis
├── utils/
│   ├── dbt_log_parser.py          # Advanced dbt log parsing & analysis
│   ├── bq_storage.py              # BigQuery error storage & deduplication
│   ├── slack_monitoring.py        # Intelligent Slack notifications
│   ├── storage.py                 # GCS log retrieval utilities
│   └── orchestration_log_parser.py # Orchestrator context extraction
├── main.py                     # Primary execution handler
├── Dockerfile                 # Container configuration
└── requirements.txt            # Dependencies
```

## Key Features

### Smart Error Detection
- Extracts table names, schemas, error types from logs
- Identifies affected models and dependencies
- Provides suggested actions for common errors

### Multi-Persona Summaries
- **Engineers**: Technical details, stack traces, fix commands
- **Analysts**: Business impact, affected reports
- **Data Scientists**: Data pipeline implications

### Production Ready
- Handles Gemini API failures gracefully
- Deduplicates messages
- Processes messages in batches
- Full error history in BigQuery

## Deployment

The agent is automatically deployed via GitHub Actions on merge to main. See `.github/workflows/deploy-log-agent.yml`.

## Configuration

Set these environment variables in Cloud Run:
- `GEMINI_API_KEY`
- `SLACK_WEBHOOK_URL`
- `BIGQUERY_DATASET`

## Example

**Input**: DBT error log
```
Database Error in model 'analytics.revenue_forecast'
relation "raw.sales_data" does not exist
```

**Output**: Slack notification
```
🔴 DBT Error Alert

Model: analytics.revenue_forecast
Error: Missing source table
Impact: Revenue dashboards will be stale

For Engineers: Run `dbt run -s +analytics.revenue_forecast --full-refresh`
For Analysts: Revenue forecasts unavailable until fixed
```

## Cost

- ~$0.02 per error analyzed (Gemini API)
- Minimal Cloud Run and BigQuery costs
- Typically <$50/month for most teams

## Future Work

- Add support for more orchestration tools (Airflow or any custom orchestrator)
- Integrate with dbt MCP sever for enhanced context
- build custom tests for better error detection
- Build vector database for error history
- Add rows related to errors to improve context
- Progress log agent from summary to root cause analysis
- Progress lgo agent from root cause analysis to automated fixes
