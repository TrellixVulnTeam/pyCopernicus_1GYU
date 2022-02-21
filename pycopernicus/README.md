# Sentinel 5P

```
curl --location --request POST '127.0.0.1:5000/sentinel5p' \
--form 'xmin="40.873292"' \
--form 'ymin="16.850661"' \
--form 'xmax="40.742011"' \
--form 'ymax="17.192127"' \
--form 'product="CO"'
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


```
curl --location --request POST '127.0.0.1:5000/vegetation' \
--header 'Authorization: Basic YWRtaW46Z2Vvc2VydmVy' \
--form 'xmin="40.873292"' \
--form 'ymin="16.850661"' \
--form 'xmax="40.742011"' \
--form 'ymax="17.192127"' \
--form 'product="NDVI1"'
```


