import osm2gmns as og

# load network from osm file
net = og.getNetFromFile("map.osm", POI=True, default_lanes=True, default_speed=True)
og.outputNetToCSV(net, 'gravity')
