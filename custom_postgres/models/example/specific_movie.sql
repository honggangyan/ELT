{% set film_title = 'Dunkirk' %}

SELECT * 
FROM {{ ref('films_view') }}
WHERE title = '{{ film_title }}'
