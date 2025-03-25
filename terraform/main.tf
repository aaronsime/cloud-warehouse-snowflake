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
      version = "~> 0.100"
    }
  }
}

provider "snowflake" {
  account_name      = var.account_name
  organization_name = var.organization_name

  user     = var.snowflake_user
  password = var.snowflake_password
  role     = var.snowflake_role
}
