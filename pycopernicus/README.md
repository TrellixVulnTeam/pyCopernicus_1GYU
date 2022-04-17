# Sentinel 5P

## Update GeoServer
```
curl --location --request POST 'http://127.0.0.1:5001/pollution' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'product=CO' \
--data-urlencode 'xmin=15.6285' \
--data-urlencode 'ymin=39.7264' \
--data-urlencode 'xmax=18.5742' \
--data-urlencode 'ymax=41.9840'
```

zona geografica indicata dalle coordinate nel sistema di riferimento EPSG:4326 bbox:

- xmin, ymin
- xmax, ymax

dove i prodotti che possiamo indicare sono:

- CO: Carbon Monoxide (CO)
- NO2: Nitrogen Dioxide (NO2)
- SO2: Sulfur Dioxide (SO2)
- CH4: Methane (CH4)
- HCHO: Formaldehyde (HCHO)
- AER: UV Aerosol Index


