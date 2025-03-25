resource "snowflake_grant_privileges_to_account_role" "file_format_usage" {
  privileges        = ["USAGE"]
  account_role_name = "TERRAFORM_ROLE"

  on_schema_object {
    object_type = "FILE FORMAT"
    object_name = "\"DEV_CLOUD_DATAWAREHOUSE\".\"RAW\".\"CSV_FORMAT\""
  }
}


