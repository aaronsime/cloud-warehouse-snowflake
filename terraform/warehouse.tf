resource "snowflake_database" "cloud_warehouse" {
  name    = "CLOUD_DATAWAREHOUSE"
  comment = "Main warehouse for all data zones"
}
