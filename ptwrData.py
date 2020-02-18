# Jack DeGuglielmo
# University of Massachusetts Amherst '21
# MIRSL
# 2/12/2020

import pyart
from pyart.core.radar import Radar
import netCDF4
import numpy as np

def read_ptwrCDF(filename):
	"""
	Takes the filepath to a MIRSL netcdf file as input.
	Returns a pyart Radar object.
	(Designed for ptwr data netcdfs)

	References: 'pyart/pyart/io/cfradial.py'
		    'pyart/pyart/core/radar.py'
	"""
	
	# Read ptwr cdf	
	ncobj = netCDF4.Dataset(filename)
	ncvars = ncobj.variables
	#print(ncvars)

	
	# coordinate variables -> create attribute dictionaries
	time = _ncvar_to_dict(ncvars['Time'])				# Probably have to add the usec part
	Usecs = _ncvar_to_dict(ncvars['Usecs'])				# Probably have to add the usec part
	timeIt = 0
	for item in time["data"]:
		#print(item)
		timeIt = timeIt + 1
	
	#_range = _ncvar_to_dict(ncvars['range'])
	#print(time)
	#print(time["data"])
	#for key,value in time.items():
	#	print(key)


	#----------------------------- Unsure about this metadata thing ------------------------------
	# 4.1 Global attribute -> move to metadata dictionary
	metadata = dict([(k, getattr(ncobj, k)) for k in ncobj.ncattrs()])
	if 'n_gates_vary' in metadata:
		metadata['n_gates_vary'] = 'false'  # corrected below

	# 4.2 Dimensions (do nothing)

	# 4.3 Global variable -> move to metadata dictionary
	if 'volume_number' in ncvars:
		metadata['volume_number'] = int(ncvars['volume_number'][:])
	else:
		metadata['volume_number'] = 0

	global_vars = {'platform_type': 'fixed', 'instrument_type': 'radar',
		   'primary_axis': 'axis_z'}
	# ignore time_* global variables, these are calculated from the time
	# variable when the file is written.
	for var, default_value in global_vars.items():
		if var in ncvars:
			metadata[var] = str(netCDF4.chartostring(ncvars[var][:]))
	else:
		metadata[var] = default_value
	#----------------------------------------------------------------------------------------------
	
	
	i = 0
	gatewidth = _ncvar_to_dict(ncvars['GateWidth'])
	#print(gatewidth)
	#print("test", gatewidth.data[0])
	rangeIt = 0
	for item in gatewidth["data"]:
		print(item * rangeIt)
		rangeIt = rangeIt + 1
	"""
	for key in gatewidth.items():
		if(i>0):
			print(key)
			print("OKAYYYYY")
			print(gatewidth[key][0])
		i=i+1
		print(i)
	"""
	
	
	
	
	fields = None
	scan_type = None
	latitude = None
	longitude = None
	altitude = None
	sweep_number = None
	sweep_mode = None
	fixed_angle = None
	sweep_start_ray_index = None
	sweep_end_ray_index = None
	azimuth = None
	elevation = None

	return Radar(time, _range, fields, metadata, scan_type,
                 latitude, longitude, altitude,

                 sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index,
                 sweep_end_ray_index,

                 azimuth, elevation,

                 altitude_agl=None,
                 target_scan_rate=None, rays_are_indexed=None,
                 ray_angle_res=None,

                 scan_rate=None, antenna_transition=None,

                 instrument_parameters=None,
                 radar_calibration=None,

                 rotation=None, tilt=None, roll=None, drift=None, heading=None,
                 pitch=None, georefs_applied=None,

                 )


def _ncvar_to_dict(ncvar, lazydict=False):
    """ Convert a NetCDF Dataset variable to a dictionary. """
    # copy all attribute except for scaling parameters
    d = dict((k, getattr(ncvar, k)) for k in ncvar.ncattrs()
             if k not in ['scale_factor', 'add_offset'])
    data_extractor = _NetCDFVariableDataExtractor(ncvar)
    if lazydict:
        d = LazyLoadDict(d)
        d.set_lazy('data', data_extractor)
    else:
        d['data'] = data_extractor()
    return d

class _NetCDFVariableDataExtractor(object):
    """
    Class facilitating on demand extraction of data from a NetCDF variable.

    Parameters
    ----------
    ncvar : netCDF4.Variable
        NetCDF Variable from which data will be extracted.

    """

    def __init__(self, ncvar):
        """ initialize the object. """
        self.ncvar = ncvar

    def __call__(self):
        """ Return an array containing data from the stored variable. """
        data = self.ncvar[:]
        if data is np.ma.masked:
            # If the data is a masked scalar, MaskedConstant is returned by
            # NetCDF4 version 1.2.3+. This object does not preserve the dtype
            # and fill_value of the original NetCDF variable and causes issues
            # in Py-ART.
            # Rather we create a masked array with a single masked value
            # with the correct dtype and fill_value.
            self.ncvar.set_auto_mask(False)
            data = np.ma.array(self.ncvar[:], mask=True)
        # Use atleast_1d to force the array to be at minimum one dimensional,
        # some version of netCDF return scalar or scalar arrays for scalar
        # NetCDF variables.
        return np.atleast_1d(data)





read_ptwrCDF('X20191016232920Z.nc')
