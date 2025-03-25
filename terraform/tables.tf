resource "snowflake_table" "olist_orders" {
  name     = "OLIST_ORDERS"
  database = "DEV_CLOUD_DATAWAREHOUSE"
  schema   = "RAW"

  column {
    name = "order_id"
    type = "STRING"
  }

  column {
    name = "customer_id"
    type = "STRING"
  }

  column {
    name = "order_status"
    type = "STRING"
  }

  column {
    name = "order_purchase_timestamp"
    type = "TIMESTAMP_NTZ"
  }

  column {
    name = "order_approved_at"
    type = "TIMESTAMP_NTZ"
  }

  column {
    name = "order_delivered_carrier_date"
    type = "TIMESTAMP_NTZ"
  }

  column {
    name = "order_delivered_customer_date"
    type = "TIMESTAMP_NTZ"
  }

  column {
    name = "order_estimated_delivery_date"
    type = "TIMESTAMP_NTZ"
  }

  comment = "Olist orders raw table"
}
