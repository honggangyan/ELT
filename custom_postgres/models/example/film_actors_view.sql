{{
    config(
        materialized='view'
    )
}}

SELECT * FROM {{ source('destination_db', 'film_actors') }}
