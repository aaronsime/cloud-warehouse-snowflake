resource "snowflake_account_role" "gcp_user_role" {
  name = "GCP_USER_ROLE"
}

resource "snowflake_account_role" "dbt_role" {
  name = "DBT_ROLE"
}
