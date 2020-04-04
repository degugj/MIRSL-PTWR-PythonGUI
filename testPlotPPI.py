"""
====================================
Create a PPI plot from a Sigmet file
====================================

An example which creates a PPI plot of a Sigmet file.

"""
print(__doc__)

import ptwrData
import matplotlib.pyplot as plt
import pyart


# create the plot using RadarDisplay (recommended method)
radar = ptwrData.read_ptwrCDF('X20191016232920Z.nc')

display = pyart.graph.RadarDisplay(radar)
fig = plt.figure()
ax = fig.add_subplot(111)
display.plot('reflectivity', 0, vmin=-32, vmax=64.)
#display.plot_range_rings([10, 20, 30, 40])
#display.plot_cross_hair(5.)
plt.show()

