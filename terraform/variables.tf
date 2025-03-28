variable "database" {
  description = "The name of the Snowflake database"
  type        = string
}

variable "snowflake_user" {
  description = "The Snowflake user to authenticate with"
  type        = string
}

variable "snowflake_password" {
  description = "The password for the Snowflake user"
  type        = string
  sensitive   = true
}

variable "snowflake_role" {
  description = "The role to use when connecting to Snowflake"
  type        = string
}

variable "gcp_bucket" {
  description = "The GCP bucket to use for staging"
  type        = string
}

variable "account_name" {
  description = "The Snowflake account name"
  type        = string
}

variable "organization_name" {
  description = "The Snowflake organization name"
  type        = string
}

variable "gcp_snowflake_password" {
  description = "The password for the GCP Snowflake user"
  type        = string
  sensitive   = true
}

variable "warehouse" {
  description = "The Snowflake warehouse to use"
  type        = string
}
