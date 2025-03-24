terraform {
  cloud {
    organization = "aaronpersonal"

    workspaces {
      name = "$TF_WORKSPACE"
    }
  }

  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.67"
    }
  }
}

provider "snowflake" {
  account_name = var.account
  region       = var.region
  cloud        = var.cloud_provider

  username = var.snowflake_user
  password = var.snowflake_password
  role     = var.snowflake_role
}

