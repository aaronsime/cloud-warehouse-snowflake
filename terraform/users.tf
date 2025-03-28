resource "snowflake_user" "gcp_user" {
  name         = "GCP_USER"
  password     = var.gcp_snowflake_password
  login_name   = "GCP_USER"
  default_role = snowflake_role.gcp_loader_role.name
  default_warehouse = var.warehouse
  must_change_password = false
}

resource "snowflake_role" "gcp_loader_role" {
  name = "GCP_LOADER_ROLE"
}

resource "snowflake_grant_privileges_to_account_role" "gcp_loader_role_grants" {
  account_role_name = snowflake_role.gcp_loader_role.name

  on_schema {
    all_schemas_in_database = var.database
  }

  privileges = ["USAGE", "CREATE STAGE", "CREATE FILE FORMAT", "CREATE TABLE", "INSERT"]
}

resource "snowflake_role_grants" "grant_loader_user_role" {
  role_name = snowflake_role.gcp_loader_role.name
  users     = [snowflake_user.gcp_user.name]
}
