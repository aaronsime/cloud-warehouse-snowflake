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
    object_name = var.warehouse
  }
}

resource "snowflake_grant_privileges_to_account_role" "compute_wh_operate" {
  account_role_name = snowflake_account_role.gcp_user_role.name
  privileges        = ["OPERATE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = var.warehouse
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_table_insert" {
  account_role_name = snowflake_account_role.gcp_user_role.name
  privileges        = ["INSERT"]

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "\"DEV_CLOUD_DATAWAREHOUSE\".\"RAW\""
    }
  }
}

##### DBT ROLE GRANTS #####
resource "snowflake_grant_privileges_to_account_role" "warehouse_usage" {
  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = var.warehouse
  }
}

resource "snowflake_grant_privileges_to_account_role" "database_usage" {
  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "DATABASE"
    object_name = var.database
  }
}

resource "snowflake_grant_privileges_to_account_role" "schema_usage" {
  for_each = toset(["RAW", "STAGING", "INTERMEDIATE", "CONSUME", "AARON_SANDBOX"])

  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE VIEW"]

  on_schema {
    schema_name = "${var.database}.${each.value}"
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_table_privileges" {
  for_each = toset(["RAW", "STAGING", "INTERMEDIATE", "CONSUME", "AARON_SANDBOX"])

  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE"]

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${var.database}.${each.value}"
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "existing_raw_tables" {
  for_each = toset(["RAW", "STAGING", "INTERMEDIATE", "CONSUME", "AARON_SANDBOX"])
  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE"]

  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "${var.database}.${each.value}"
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "existing_views" {
  for_each = toset(["RAW", "STAGING", "INTERMEDIATE", "CONSUME", "AARON_SANDBOX"])
  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["SELECT"]

  on_schema_object {
    all {
      object_type_plural = "VIEWS"
      in_schema          = "${var.database}.${each.value}"
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_view_privileges" {
  for_each = toset(["RAW", "STAGING", "INTERMEDIATE", "CONSUME", "AARON_SANDBOX"])

  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["SELECT"]

  on_schema_object {
    future {
      object_type_plural = "VIEWS"
      in_schema          = "${var.database}.${each.value}"
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "create_table_schema_privileges" {
  for_each = toset(["RAW", "STAGING", "INTERMEDIATE", "CONSUME", "AARON_SANDBOX"])

  account_role_name = snowflake_account_role.dbt_role.name
  privileges        = ["CREATE TABLE"]

  on_schema {
    schema_name = "${var.database}.${each.value}"
  }
}
