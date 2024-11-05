{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['zpid'],
    merge_update_columns=[
        'zpid',
        'address',
        'detailurl',
        'lotid',
        'imgsrc',
        'price',
        'zip',
        'buildingname',
        'propertytype',
        'bathrooms',
        'bedrooms',
        'livingarea',
        'longitude',
        'latitude',
        'UNIT',
        'UNITS',
        'updated_at'
    ]
) }}

WITH zillow_apartments AS (
    SELECT
        zpid,
        address,
        detailurl,
        lotid,
        imgsrc,
        price,
        zip,
        buildingname,
        propertytype,
        bathrooms,
        bedrooms,
        livingarea,
        longitude,
        latitude,
        UNIT,  
        UNITS,
        current_timestamp() AS apartment_added_dt,
        current_timestamp() AS updated_at
    FROM {{ source('raw', 'raw_zillow_apartments') }}
)

SELECT
    *
FROM zillow_apartments