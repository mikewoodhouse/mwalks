# mwalks

Don't know if this is the best way, but it gets Win-working versions of various useful libraries installed:

Found on [stackoverflow](https://stackoverflow.com/questions/54734667/error-installing-geopandas-a-gdal-api-version-must-be-specified-in-anaconda) and extended to include everything else needed.


```
pip install --upgrade pip

pip install wheel
pip install pipwin

pipwin install numpy
pipwin install pandas
pipwin install shapely
pipwin install gdal
pipwin install fiona
pipwin install pyproj
pipwin install six
pipwin install rtree
pipwin install geopandas
pipwin install cartopy

pip install jupyter
pip install matplotlib
pip install scipy
pip install pykdtree
```

# References

First effort stolen pretty much  verbatim from this one:
https://ocefpaf.github.io/python4oceanographers/blog/2015/08/03/fiona_gpx/

http://research.ganse.org/datasci/gps/

https://www.geodose.com/2018/04/create-gpx-tracking-file-visualizer-python.html

https://towardsdatascience.com/build-interactive-gps-activity-maps-from-gpx-files-using-folium-cf9eebba1fe7
