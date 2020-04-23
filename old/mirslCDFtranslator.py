#Jack DeGuglielmo
#MIRSL 11/22/2019

import numpy
import netCDF4
from netCDF4 import Dataset

#Create test cdf file for testing plot_one*.py script
rootgrp = Dataset("test.nc", "w", format="NETCDF4")
rootgrpOLD = Dataset("X20191016232920Z.nc", "a")

#create dimensions I guess
time = rootgrp.createDimension("time", None)
range = rootgrp.createDimension("range", None)
sweep = rootgrp.createDimension("sweep", None)
string_length_24 = rootgrp.createDimension("string_length_24", None)

#create variables as I need them in plot_one
time = rootgrp.createVariable("time", "f8", ("time",))
range = rootgrp.createVariable("range", "f8", ("range",))
latitude = rootgrp.createVariable("latitude", "f8", ("latitude",))

time[:] = rootgrpOLD.variables["Time"][:]

latitude = rootgrpOLD.attributes["Latitude"][:]

i = 0
offset = time[0]
while i < len(time):
	#time equals time minus start time (converting to relative time)
	#adding Usec to get double time
	time[i] = time[i] + (rootgrpOLD.variables["Usecs"][i]/1000000) - offset
	
	range[i] = 0	
	
	i += 1
#print(time)


rootgrp.close()
