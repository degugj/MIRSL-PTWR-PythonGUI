# Jack DeGuglielmo
# University of Massachusetts Amherst '21
# MIRSL
# 2/12/2020

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
	pyart.load_config('/home/jdegug/MIRSL-PTWR-PythonGUI/ptwr_config.py')
	

	# Read ptwr cdf	
	ncobj = netCDF4.Dataset(filename)
	ncvars = ncobj.variables
	#print(ncvars)

	
	# coordinate variables -> create attribute dictionaries
	time = _ncvar_to_dict(ncvars['Time'])				# Probably have to add the usec part
	Usecs = _ncvar_to_dict(ncvars['Usecs'])				# Probably have to add the usec part
	
	#_range = _ncvar_to_dict(ncvars['range'])
	#print(time)
	#print(time["data"])
	#for key,value in time.items():
	#	print(key)


	#----------------------------- Unsure about this metadata thing ------------------------------
	# 4.1 Global attribute -> move to metadata dictionary
	metadata = dict([(k, getattr(ncobj, k)) for k in ncobj.ncattrs()])


	# 4.2 Dimensions (do nothing)

	# 4.3 Global variable -> move to metadata dictionary SUSPECT
	if 'volume_number' in ncvars:
		metadata['volume_number'] = int(ncvars['volume_number'][:])
	else:
		metadata['volume_number'] = 0

	
	#----------------------------------------------------------------------------------------------
	
	scan_type = 'ppi'
	
	i = 0
	gatewidth = _ncvar_to_dict(ncvars['GateWidth'])
	_range = gatewidth
	#print(gatewidth)
	#print("test", gatewidth.data[0])
	rangeIt = 0
	for item in gatewidth["data"]:
		#print(item * rangeIt)
		_range["data"][rangeIt] = (item * rangeIt)/1000
		rangeIt = rangeIt + 1
		
	#print(_range)
	sweep_number = {'data': np.ma.array([0], mask=False)};
	
	"""
	for key in gatewidth.items():
		if(i>0):
			print(key)
			print("OKAYYYYY")
			print(gatewidth[key][0])
		i=i+1
		print(i)
	"""
    
	metadata = dict([(k, getattr(ncobj, k)) for k in ncobj.ncattrs()])
	if 'n_gates_vary' in metadata:
		metadata['n_gates_vary'] = 'false'  # corrected below

	# 4.2 Dimensions (do nothing)

	
	# 4.10 Moments field data variables -> field attribute dictionary
	if 'ray_n_gates' in ncvars:
		# all variables with dimensions of n_points are fields.
		keys = [k for k, v in ncvars.items()
				if v.dimensions == ('n_points', )]
	else:
		# all variables with dimensions of 'time', 'range' are fields
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
		

	#fields = None
	#scan_type = None
	latitude = None
	longitude = None
	altitude = None
	#sweep_number = None
	sweep_mode = None
	fixed_angle = None
	sweep_start_ray_index = None
	sweep_end_ray_index = None
	azimuth = None
	elevation = None

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
	
	
	
	#print(ncvars['Reflectivity'])
	
	reflectivity = _ncvar_to_dict(ncvars['Reflectivity'])
	

	#print(ncvars['Reflectivity'])
	#print(reflectivity['data'][1])
	radar.ngates = 626;
	radar.nrays = 438;
	radar.add_field('reflectivity', reflectivity)
	
	radar.altitude = {'Units': 'meters', 'data': [144]}
	radar.latitude = {'Units': 'degrees', 'data': [42.3909]}
	radar.longitude = {'Units': 'degrees', 'data': [-72.5195]}
	radar.azimuth = _ncvar_to_dict(ncvars['Azimuth'])
	radar.elevation = _ncvar_to_dict(ncvars['Elevation'])
	#radar.info()             
	
	radar.time = {'units': 'seconds since 2020-02-13T00:28:55Z', 'data': radar.time['data']}
	
	usecs = _ncvar_to_dict(ncvars['Usecs'])
	test = []
	for i in range(len(usecs['data'])):
		#print(radar.time['data'][i] + usecs['data'][i]/1000000)
		#print(radar.time['data'][i] + (usecs['data'][i]/1000000))		
		test.append(radar.time['data'][i] + (usecs['data'][i]/1000000))
		#print(test[i])
		
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





radar = read_ptwrCDF('X20191016232920Z.nc')




#PLOT ONE GRID EXAMPLE

# mask out last 10 gates of each ray, this removes the "ring" around th radar.
radar.fields['reflectivity']['data'][:, -10:] = np.ma.masked

# exclude masked gates from the gridding
gatefilter = pyart.filters.GateFilter(radar)
gatefilter.exclude_transition()
gatefilter.exclude_masked('reflectivity')

# perform Cartesian mapping, limit to the reflectivity field.
grid = pyart.map.grid_from_radars(
    (radar,), gatefilters=(gatefilter, ),
    grid_shape=(1, 3500, 3500),
    grid_limits=((1, 5000), (-123000.0, 123000.0), (-123000.0, 123000.0)),
    fields=['reflectivity'])

# create the plot
fig = plt.figure()
ax = fig.add_subplot(111)
ax.imshow(grid.fields['reflectivity']['data'][0], origin='lower')
plt.show()


