resource "snowflake_file_format" "csv_format" {
  name         = "CSV_FORMAT"
  database     = "DEV_CLOUD_DATAWAREHOUSE"
  schema       = "RAW"
  format_type  = "CSV"
  skip_header  = 1
  field_optionally_enclosed_by = "\""
}

resource "snowflake_stage" "raw_stage" {
  name      = "RAW_STAGE"
  database  = var.database
  schema    = "RAW"

  url                 = "gcs://outbound-snowflake-dev/raw/incoming"
  storage_integration = "GCS_INT"

  file_format = "FORMAT_NAME = DEV_CLOUD_DATAWAREHOUSE.RAW.CSV_FORMAT"

  comment = "Stage for raw olist incoming data"
}

