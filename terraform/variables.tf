variable "database" {
  description = "The name of the Snowflake database"
  type        = string
}

variable "region" {
  description = "The region where the Snowflake account is located"
  type        = string
}

variable "account" {
  description = "The Snowflake account name"
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