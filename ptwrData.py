# Jack DeGuglielmo
# University of Massachusetts Amherst '21
# MIRSL
# 2/12/2020

"""
ptwrData.py
===========
This script contains functions necessary to interface with a PTWR object.
The file can be imported into other scripts to access functions like read_ptwrCDF to instantiate a radar obect from a .nc file.
See testGridPlot.py as an example.
"""

import pyart
from pyart.core.radar import Radar
import netCDF4
import numpy as np
import matplotlib.pyplot as plt

def read_ptwrCDF(filename):
	"""
	Takes the filepath to a MIRSL netcdf file as input.
	Returns a pyart Radar object.
	(Designed for ptwr data netcdfs)

	References: 'pyart/pyart/io/cfradial.py'
		    'pyart/pyart/core/radar.py'
	"""
	pyart.load_config('/home/jdegug/MIRSL-PTWR-PythonGUI/ptwr_config.py')	# Unclear if we actually need this
	
	# netCDF4 functions to obtain nc fields and vars
	ncobj = netCDF4.Dataset(filename)
	ncvars = ncobj.variables

	
	# obtaining time and microseconds to later be merged as one time variable
	time = _ncvar_to_dict(ncvars['Time'])			
	Usecs = _ncvar_to_dict(ncvars['Usecs'])
	
	
	metadata = dict([(k, getattr(ncobj, k)) for k in ncobj.ncattrs()])	# loads our metadata into radar objects. Also may not be necessary

	if 'volume_number' in ncvars:
		metadata['volume_number'] = int(ncvars['volume_number'][:])
	else:
		metadata['volume_number'] = 0
	
	scan_type = 'ppi'	# identifying scan type; may not be constant
	

	gatewidth = _ncvar_to_dict(ncvars['GateWidth'])
	


	_range = gatewidth		# initializing range as gatewidth for convenience
	rangeIt = 0

	# calculating range using gatewidth times iterator
	for item in gatewidth["data"]:
		_range["data"][rangeIt] = (item * rangeIt)/1000		# must divide by 100 as Gatewidth is in mm
		rangeIt = rangeIt + 1
		
	sweep_number = {'data': np.ma.array([0], mask=False)};


    
	metadata = dict([(k, getattr(ncobj, k)) for k in ncobj.ncattrs()])
	if 'n_gates_vary' in metadata:
		metadata['n_gates_vary'] = 'false'

	
	if 'ray_n_gates' in ncvars:
		keys = [k for k, v in ncvars.items()
				if v.dimensions == ('n_points', )]
	else:
		keys = [k for k, v in ncvars.items()
				if v.dimensions == ('time', 'range')]
                
	fields = {}
	for key in keys:
		field_name = filemetadata.get_field_name(key)
		if field_name is None:
			if exclude_fields is not None and key in exclude_fields:
				if key not in include_fields:
					continue
			if include_fields is None or key in include_fields:
				field_name = key
			else:
				continue
		fields[field_name] = _ncvar_to_dict(ncvars[key], delay_field_loading)
		
	

	latitude = None
	longitude = None
	altitude = None
	sweep_mode = None
	fixed_angle = None
	sweep_start_ray_index = None
	sweep_end_ray_index = None
	azimuth = None
	elevation = None


	# instantiating a new radar object with empty fields... would rather intantiate while returning
	radar = Radar(time, _range, fields, metadata, scan_type,
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
	
	
	

	# filling radar object with remaining fields
	
	reflectivity = _ncvar_to_dict(ncvars['Reflectivity'])
	
	radar.ngates = 626;
	radar.nrays = 438;
	radar.add_field('reflectivity', reflectivity)
	
	radar.altitude = {'Units': 'meters', 'data': [144]}
	radar.latitude = {'Units': 'degrees', 'data': [42.3909]}
	radar.longitude = {'Units': 'degrees', 'data': [-72.5195]}
	radar.azimuth = _ncvar_to_dict(ncvars['Azimuth'])
	radar.elevation = _ncvar_to_dict(ncvars['Elevation'])
	
	radar.time = {'units': 'seconds since 2020-02-13T00:28:55Z', 'data': radar.time['data']}	# must be changed (cannot hard code the seconds since)
	
	usecs = _ncvar_to_dict(ncvars['Usecs'])
	test = []
	for i in range(len(usecs['data'])):
		test.append(radar.time['data'][i] + (usecs['data'][i]/1000000))
		
	radar.time = {'units': 'seconds since 2020-02-13T00:28:55Z', 'data': test[:]}
		
	
	print(radar.info('full'))
	print("----- For Scott -----")
	print(radar.range['data'].mean())
	
	return radar;




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

