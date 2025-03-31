resource "snowflake_grant_privileges_to_account_role" "file_format_usage" {
  privileges        = ["USAGE"]
  account_role_name = "TERRAFORM_ROLE"

  on_schema_object {
    object_type = "FILE FORMAT"
    object_name = "\"DEV_CLOUD_DATAWAREHOUSE\".\"RAW\".\"CSV_FORMAT\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "raw_stage_usage" {
  account_role_name = snowflake_account_role.gcp_user_role.name
  privileges        = ["USAGE", "READ"]

  on_schema_object {
    object_type  = "STAGE"
    object_name  = "\"DEV_CLOUD_DATAWAREHOUSE\".\"RAW\".\"RAW_STAGE\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "gcs_int_usage" {
  account_role_name = snowflake_account_role.gcp_user_role.name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "INTEGRATION"
    object_name = "GCS_INT"
  }
}

resource "snowflake_grant_privileges_to_account_role" "csv_format_usage" {
  account_role_name = snowflake_account_role.gcp_user_role.name
  privileges        = ["USAGE"]

  on_schema_object {
    object_type = "FILE FORMAT"
    object_name = "\"DEV_CLOUD_DATAWAREHOUSE\".\"RAW\".\"CSV_FORMAT\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "compute_wh_usage" {
  account_role_name = snowflake_account_role.gcp_user_role.name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = "COMPUTE_WH"
  }
}

resource "snowflake_grant_privileges_to_account_role" "compute_wh_operate" {
  account_role_name = snowflake_account_role.gcp_user_role.name
  privileges        = ["OPERATE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = "COMPUTE_WH"
  }
}
