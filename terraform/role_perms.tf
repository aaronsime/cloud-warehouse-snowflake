resource "snowflake_grant_privileges" "csv_file_format_usage" {
  privileges     = ["USAGE"]
  on {
    object_type = "FILE FORMAT"
    object_name = "\"DEV_CLOUD_DATAWAREHOUSE\".\"RAW\".\"CSV_FORMAT\""
  }
  to {
    role = "TERRAFORM_ROLE"
  }
}

