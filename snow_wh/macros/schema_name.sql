{% macro generate_schema_name(custom_schema_name, node) %}
    {# If a custom schema is defined (via +schema), use it. Otherwise fallback to target.schema #}
    {{ custom_schema_name if custom_schema_name is not none else target.schema }}
{% endmacro %}
