resource "snowflake_account_role" "gcp_user_role" {
  name = "GCP_USER_ROLE"
}

resource "snowflake_user" "gcp_user" {
  name              = "GCP_USER"
  login_name        = "GCP_USER"
  password          = var.gcp_snowflake_password
  default_role      = snowflake_account_role.gcp_user_role.name
  default_warehouse = var.warehouse
  must_change_password = false
}

resource "snowflake_grant_account_role" "gcp_user_grant" {
  role_name = snowflake_account_role.gcp_user_role.name
  user_name = snowflake_user.gcp_user.name
}

resource "snowflake_grant_privileges_to_account_role" "gcp_user_schema_grants" {
  account_role_name = snowflake_account_role.gcp_user_role.name

  on_schema {
    all_schemas_in_database = var.database
  }

  privileges = [
    "USAGE",
    "CREATE STAGE",
    "CREATE FILE FORMAT",
    "CREATE TABLE"
  ]
}

resource "snowflake_grant_privileges_to_account_role" "future_table_insert" {
  privileges        = ["INSERT"]
  account_role_name = snowflake_account_role.gcp_user_role.name

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${var.database}.RAW"
    }
  }
}
