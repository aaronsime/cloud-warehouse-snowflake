{%- macro generate_dim_consume_view(dim_model, exclude_cols=none) -%}
SELECT
    {% if exclude_cols %}
        {{ dbt_utils.star(from=dim_model, except=exclude_cols) }}
    {% else %}
        {{ dbt_utils.star(from=dim_model) }}
    {% endif %}
FROM {{ dim_model }}
{%- endmacro -%}
