# Jack DeGuglielmo
# University of Massachusetts Amherst '21
# MIRSL
# 2/12/2020

import ptwrData
import pyart
import netCDF4
import numpy as np
import matplotlib.pyplot as plt

radar = ptwrData.read_ptwrCDF('X20191016232920Z.nc')

#PLOT ONE GRID EXAMPLE

# mask out last 10 gates of each ray, this removes the "ring" around th radar.
#radar.fields['reflectivity']['data'][:, -10:] = np.ma.masked

# exclude masked gates from the gridding
radar.info()


gatefilter = pyart.filters.GateFilter(radar)
gatefilter.exclude_transition()
gatefilter.exclude_masked('reflectivity')

display = pyart.graph.RadarDisplay(radar)
display.plot_ppi('reflectivity')
plt.show()
#radar.range['data'] = np.linspace(0.0, 96.*(626-1), 626)
print(radar.gate_y['data'])
# perform Cartesian mapping, limit to the reflectivity field.
grid = pyart.map.grid_from_radars(
    (radar,),
    grid_shape=(3, 100, 100),
    grid_limits=((1000., 4000), (-50000.0, 50000.0), (-50000.0, 50000.0)),
    fields=['reflectivity'])

grid_disp = pyart.graph.GridMapDisplay(grid)
grid_disp.plot_grid('reflectivity')
plt.show()
# create the plot
#fig = plt.figure()
#ax = fig.add_subplot(111)
#ax.imshow(grid.fields['reflectivity']['data'][1])
#plt.xlim(2000,3000)
#plt.ylim(2000,3000)
#plt.show()

