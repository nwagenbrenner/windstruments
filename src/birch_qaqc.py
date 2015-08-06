#!/usr/bin/env python

import birch
import zipfile
import os

plot = 'BC-49'

start_time = '2013-06-19T22:00:00'
end_time = '2013-06-21T23:00:00'
ignore_crappy = True

point = birch.mean_flow_point(plot, start_time, end_time, ignore_crappy)
point.create_time_series_image()


#field = birch.mean_flow_field(start_time, end_time, True)
#field.create_kmz('aug15_birch.kmz', True)




