from setuptools import setup, find_packages

setup(
    name='pyGeoServer',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'geopandas', 'xmltodict', 'shapely', 
                      'attrs', 'netCDF4', 'SQLAlchemy', 'geoserver-rest', 
                      'GeoAlchemy2', 'xarray', 'numpy', 'pandas', 
                      'geopandas', 'dask', 'h5netcdf', 'scipy', 'pygeos']
)