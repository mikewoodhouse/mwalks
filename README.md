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
pip install seaborn

pip install pytest
pip install flake8
```

# References

First effort stolen pretty much  verbatim from this one:
https://ocefpaf.github.io/python4oceanographers/blog/2015/08/03/fiona_gpx/

http://research.ganse.org/datasci/gps/

https://www.geodose.com/2018/04/create-gpx-tracking-file-visualizer-python.html

https://towardsdatascience.com/build-interactive-gps-activity-maps-from-gpx-files-using-folium-cf9eebba1fe7

## GPX Files

* `<trk>` is track. Within that,
* `<trkseg>` is a track segment. I'm guessing there may be more than one of these, although my files look to have one. Within that, I'm seeing lots of
* `<trkpt>` with attributes "lat" and "lon" and contents of `<ele>` (elevation) and `<time>` stamps. No distance (or velocity) information, so something to calculate the distance between two `<trkpt>`s is going to be needed

## Distance Calculation

The Haversine formula:

See: http://www.movable-type.co.uk/scripts/latlong.html

a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
c = 2 ⋅ atan2( √a, √(1−a) )
d = R ⋅ c
where φ is latitude, λ is longitude, R is earth's radius (mean radius = 6,371km); note that angles need to be in radians to pass to trig functions!

JavaScript:
```
const R = 6371e3; // metres
const φ1 = lat1 * Math.PI/180; // φ, λ in radians
const φ2 = lat2 * Math.PI/180;
const Δφ = (lat2-lat1) * Math.PI/180;
const Δλ = (lon2-lon1) * Math.PI/180;

const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
          Math.cos(φ1) * Math.cos(φ2) *
          Math.sin(Δλ/2) * Math.sin(Δλ/2);
const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

const d = R * c; // in metres
```