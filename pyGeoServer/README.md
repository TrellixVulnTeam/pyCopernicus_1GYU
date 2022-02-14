# list stores
```
curl -v -u admin:geoserver http://localhost/geoserver/rest/workspaces/test/coveragestores
```

# create coverage store
```
curl -v -u admin:geoserver -XPOST \
    -H "Content-type: application/json" \
    -d '{"coverageStore":{"name":"myCoverageStore","type":"NetCDF","enabled":true,"_default":false,"workspace":{"name":"test"},"url":"file:test\/SSP2_10dollarsboth.nc"}}' \
    http://localhost/geoserver/rest/workspaces/test/coveragestores
```

# update store coverage
```
curl -v -u admin:geoserver -XPUT \
    -H "Content-Type: application/zip" \
    -H "Accept: application/json" \
    --data-binary @/my-netcdf-file.nc.zip \
    http://localhost/geoserver/rest/workspaces/test/coveragestores/myCoverageStore/file.netcdf?configure=none
```

```
curl --location --request POST '127.0.0.1:5000/sentinel5p' \
--header 'Authorization: Basic YWRtaW46Z2Vvc2VydmVy' \
--form 'xmin="40.873292"' \
--form 'ymin="16.850661"' \
--form 'xmax="40.742011"' \
--form 'ymax="17.192127"' \
--form 'product="CO"'
```

