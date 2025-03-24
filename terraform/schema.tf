resource "snowflake_schema" "raw" {
  name     = "RAW"
  database = snowflake_database.cloud_warehouse.name
  comment  = "Raw files landed from external sources"
}

resource "snowflake_schema" "staging" {
  name     = "STAGING"
  database = snowflake_database.cloud_warehouse.name
  comment  = "Initial typecasted and cleaned tables"
}

resource "snowflake_schema" "intermediate" {
  name     = "INTERMEDIATE"
  database = snowflake_database.cloud_warehouse.name
  comment  = "Joined or enriched datasets"
}

resource "snowflake_schema" "consume" {
  name     = "CONSUME"
  database = snowflake_database.cloud_warehouse.name
  comment  = "Final analytical and business-facing tables"
}
