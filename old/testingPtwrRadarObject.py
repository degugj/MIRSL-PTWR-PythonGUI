# Jack DeGuglielmo
# University of Massachusetts Amherst '21
# MIRSL
# 3/9/2020

import ptwrData
import pyart
import netCDF4
import numpy as np
import matplotlib.pyplot as plt

radar = ptwrData.read_ptwrCDF('X20191016232920Z.nc')


