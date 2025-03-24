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
  account_name      = "UV98843"
  organization_name = "QMUGLJO"

  user     = var.snowflake_user
  password = var.snowflake_password
  role     = var.snowflake_role
}
