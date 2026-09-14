{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    
    {# If in dev and a custom schema is provided, use ONLY the custom schema #}
    {%- if target.name == 'dev' and custom_schema_name is not none -%}

        {{ custom_schema_name | trim }}

    {# In dev or if no custom schema is provided, fallback to the default logic #}
    {%- else -%}

        {%- if custom_schema_name is none -%}
            {{ default_schema }}
        {%- else -%}
            {{ default_schema }}_{{ custom_schema_name | trim }}
        {%- endif -%}

    {%- endif -%}

{%- endmacro %}
