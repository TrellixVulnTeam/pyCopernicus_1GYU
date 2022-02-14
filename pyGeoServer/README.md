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
