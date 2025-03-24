resource "snowflake_schema" "raw" {
  name     = "RAW"
  database = var.database
  comment  = "Raw files landed from external sources"
}

resource "snowflake_schema" "staging" {
  name     = "STAGING"
  database = var.database
  comment  = "Initial typecasted and cleaned tables"
}

resource "snowflake_schema" "intermediate" {
  name     = "INTERMEDIATE"
  database = var.database
  comment  = "Joined or enriched datasets"
}

resource "snowflake_schema" "consume" {
  name     = "CONSUME"
  database = var.database
  comment  = "Final analytical and business-facing tables"
}
