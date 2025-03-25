resource "snowflake_table" "olist_orders" {
  name     = "OLIST_ORDERS"
  database = var.database
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

resource "snowflake_table" "olist_order_items" {
  name     = "OLIST_ORDER_ITEMS"
  database = var.database
  schema   = "RAW"

  column {
    name = "order_id"
    type = "STRING"
  }

  column {
    name = "order_item_id"
    type = "STRING"
  }

  column {
    name = "product_id"
    type = "STRING"
  }

  column {
    name = "seller_id"
    type = "STRING"
  }

  column {
    name = "shipping_limit_date"
    type = "TIMESTAMP_NTZ"
  }

  column {
    name = "price"
    type = "FLOAT"
  }

  column {
    name = "freight_value"
    type = "FLOAT"
  }

  comment = "Olist order items raw table"
}

resource "snowflake_table" "olist_customers" {
  name     = "OLIST_CUSTOMERS"
  database = var.database
  schema   = "RAW"

  column {
    name = "customer_id"
    type = "STRING"
  }

  column {
    name = "customer_unique_id"
    type = "STRING"
  }

  column {
    name = "customer_zip_code_prefix"
    type = "STRING"
  }

  column {
    name = "customer_city"
    type = "STRING"
  }

  column {
    name = "customer_state"
    type = "STRING"
  }

  comment = "Olist customers raw table"
}

resource "snowflake_table" "olist_products" {
  name     = "OLIST_PRODUCTS"
  database = var.database
  schema   = "RAW"

  column {
    name = "product_id"
    type = "STRING"
  }

  column {
    name = "product_category_name"
    type = "STRING"
  }

  column {
    name = "product_name_lenght"
    type = "INT"
  }

  column {
    name = "product_description_lenght"
    type = "INT"
  }

  column {
    name = "product_photos_qty"
    type = "INT"
  }

  column {
    name = "product_weight_g"
    type = "INT"
  }

  column {
    name = "product_length_cm"
    type = "INT"
  }

  column {
    name = "product_height_cm"
    type = "INT"
  }

  column {
    name = "product_width_cm"
    type = "INT"
  }

  comment = "Olist products raw table"
}

resource "snowflake_table" "olist_sellers" {
  name     = "OLIST_SELLERS"
  database = var.database
  schema   = "RAW"

  column {
    name = "seller_id"
    type = "STRING"
  }

  column {
    name = "seller_zip_code_prefix"
    type = "STRING"
  }

  column {
    name = "seller_city"
    type = "STRING"
  }

  column {
    name = "seller_state"
    type = "STRING"
  }

  comment = "Olist sellers raw table"
}

resource "snowflake_table" "olist_geolocation" {
  name     = "OLIST_GEOLOCATION"
  database = var.database
  schema   = "RAW"

  column {
    name = "geolocation_zip_code_prefix"
    type = "STRING"
  }

  column {
    name = "geolocation_lat"
    type = "FLOAT"
  }

  column {
    name = "geolocation_lng"
    type = "FLOAT"
  }

  column {
    name = "geolocation_city"
    type = "STRING"
  }

  column {
    name = "geolocation_state"
    type = "STRING"
  }

  comment = "Olist geolocation raw table"
}

resource "snowflake_table" "olist_order_reviews" {
  name     = "OLIST_ORDER_REVIEWS"
  database = var.database
  schema   = "RAW"

  column {
    name = "review_id"
    type = "STRING"
  }

  column {
    name = "order_id"
    type = "STRING"
  }

  column {
    name = "review_score"
    type = "INT"
  }

  column {
    name = "review_comment_title"
    type = "STRING"
  }

  column {
    name = "review_comment_message"
    type = "STRING"
  }

  column {
    name = "review_creation_date"
    type = "TIMESTAMP_NTZ"
  }

  column {
    name = "review_answer_timestamp"
    type = "TIMESTAMP_NTZ"
  }

  comment = "Olist order reviews raw table"
}

resource "snowflake_table" "olist_order_payments" {
  name     = "OLIST_ORDER_PAYMENTS"
  database = var.database
  schema   = "RAW"

  column {
    name = "order_id"
    type = "STRING"
  }

  column {
    name = "payment_sequential"
    type = "INT"
  }

  column {
    name = "payment_type"
    type = "STRING"
  }

  column {
    name = "payment_installments"
    type = "INT"
  }

  column {
    name = "payment_value"
    type = "FLOAT"
  }

  comment = "Olist order payments raw table"
}


resource "snowflake_table" "product_category_translation" {
  name     = "PRODUCT_CATEGORY_TRANSLATION"
  database = var.database
  schema   = "RAW"

  column {
    name = "product_category_name"
    type = "STRING"
  }

  column {
    name = "product_category_name_english"
    type = "STRING"
  }

  comment = "Olist product category translation raw table"
}
