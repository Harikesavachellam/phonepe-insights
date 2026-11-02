# Map sources and attribution

## State boundaries

GeoJSON prepared by Josh Brobst from DataMeet India's state boundary shapefiles:

https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson

Underlying boundaries: https://github.com/datameet/maps

Attribution: India state boundaries by the DataMeet India community,
https://datameet.org/ , CC BY 4.0:
https://creativecommons.org/licenses/by/4.0/

The project adds a normalized `map_id` property. Geographic coordinates are
preserved. The mapping technique is explained in Josh Brobst's Stack Overflow
answer: https://stackoverflow.com/a/62976794 (CC BY-SA 4.0).
Project chart code was written for this app, using the documented Plotly API.

## District boundaries

https://github.com/geohacker/india/blob/master/district/india_district.geojson

The repository credits GADM: https://gadm.org/
GADM's data is available for academic and other non-commercial use; see
https://gadm.org/license.html for the applicable terms. This educational project
includes a simplified version of that older boundary reference. Do not assume it
is licensed for commercial redistribution.

Modifications: shapes simplified at 0.012 degrees with topology preservation;
only state, district and normalized `map_id` properties retained. This reduces
the source from approximately 34.5 MB to 2 MB. The 594 boundary features are older
than the PhonePe district definitions; unmatched names are explicitly reported.
