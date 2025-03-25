resource "snowflake_file_format" "csv_format" {
  name         = "CSV_FORMAT"
  database     = "DEV_CLOUD_DATAWAREHOUSE"
  schema       = "RAW"
  format_type  = "CSV"
  skip_header  = 1
  field_optionally_enclosed_by = "\""
}

resource "snowflake_storage_integration" "gcs_integration" {
  name              = "GCS_INT"
  comment           = "Storage integration for GCS"
  type              = "EXTERNAL_STAGE"
  enabled           = true
  storage_provider  = "GCS"

  storage_allowed_locations = [
    "gcs://outbound-snowflake-dev/raw/incoming"
  ]
}


resource "snowflake_stage" "raw_stage" {
  depends_on = [
    snowflake_file_format.csv_format,
    snowflake_storage_integration.gcs_integration
  ]
  name      = "RAW_STAGE"
  database  = var.database
  schema    = "RAW"

  url                 = "gcs://outbound-snowflake-dev/raw/incoming"
  storage_integration = "GCS_INT"

  file_format = "FORMAT_NAME = DEV_CLOUD_DATAWAREHOUSE.RAW.CSV_FORMAT"

  comment = "Stage for raw olist incoming data"
}
