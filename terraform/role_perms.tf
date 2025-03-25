resource "snowflake_file_format_grant" "csv_usage_grant" {
  database_name     = snowflake_file_format.csv_format.database
  schema_name       = snowflake_file_format.csv_format.schema
  file_format_name  = snowflake_file_format.csv_format.name
  privilege         = "USAGE"
  roles             = ["TERRAFORM_ROLE"]
}
