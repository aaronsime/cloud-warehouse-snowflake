{% test unique_with_rows(model, column_name) %}
-- Return every column for the rows whose {{ column_name }} is duplicated
with dups as (
    select {{ column_name }}
    from {{ model }}
    group by {{ column_name }}
    having count(*) > 1
)
select *
from {{ model }}
where {{ column_name }} in (select {{ column_name }} from dups)
{% endtest %}
