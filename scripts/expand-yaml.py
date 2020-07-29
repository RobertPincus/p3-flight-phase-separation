#! /usr/bin/env python

import datetime
import yaml
import pathlib

import xarray as xr

data_dir = pathlib.Path('/Users/robert/Dropbox/Scientific/Projects/ATOMIC:EURECA4/data')
seg_dir  = pathlib.Path('./flight_phase_files')
mini_dir = pathlib.Path('./mini-yaml')

platform = "P3"
variable = "Flight-segments"
data_version = "v0.5"

seg_types = ['transit', 'circle', 'profile', 'axbt', 'cloud']
#
# Can I get the list of dates automatically? Until then...
#
flight_dates = ['2020-01-17', '2020-01-19', '2020-01-23',
                '2020-01-24', '2020-01-31',
                '2020-02-03', '2020-02-04', '2020-02-05',
                '2020-02-09', '2020-02-10', '2020-02-11']

p3_info = {'campaign':'EUREC4A', 'activity':'ATOMIC', 'platform':'P3',
           "contacts": [{'name': 'Robert Pincus',
                        'email': 'Robert.Pincus@colorado.edu',
                        'tags': ['sc', 'dp']},
                        {'name': 'Adriana Bailey',
                        'email': 'abailey@ucar.edu',
                        'tags': ['sc', 'dp']},
                        {'name': 'Chris Fairall',
                        'email': 'Chris.Fairall@noaa.gov',
                        'tags': ['cs', 'pi']}] }

def dict_to_datetime(year, month, day, tm):
    # '''Here tm is a dict with keys hour, min, and optinally sec'''
    if 'sec' in tm.keys():
        return(datetime.datetime(year, month, day, hour=int(tm["hour"]), minute=int(tm["min"]), second=int(tm["sec"])))
    else:
        return(datetime.datetime(year, month, day, hour=int(tm["hour"]), minute=int(tm["min"])))

#Automation:
#  small YAML with segment start time, end time, type, name/description
#  Script gets a date and this small YAML, opens AC file
#  Adds header info including flight_id, TO/L times(?)
#  Sorts basic segments by time?
#  Validates segment times against AC file
#  Generates segment ID based on type

for d in flight_dates:
    year  = int(d[0:4])
    month = int(d[5:7])
    day   = int(d[8:10])
    #
    # Flight level summary file - could construct name/URL more programatically
    #
    fl_file = sorted(data_dir.joinpath("flight-level-summary/Level_2").glob("*" + d.replace('-', '')  + "*.nc"))[0]
    with fl_file as flight_level:
        f = xr.open_dataset(flight_level)
    #
    # Take-off and landing times, approach suggested by Adriana Bailey
    #
    in_air = f.where(f.alt > 80., drop=True)
    # Convert from np.datetime64 to datetime.datetimes
    takeoff_time = in_air.time[ 0].values.astype('datetime64[s]').tolist()
    landing_time = in_air.time[-1].values.astype('datetime64[s]').tolist()

    mini_files = sorted(mini_dir.glob("*" + d + "*.yaml"))
    if len(mini_files) is 0:
        print ("Mini YAML file missing, skipping date " + d)
    else:
        print("  nominal takeoff time", takeoff_time, "nominal landing time", landing_time)
        with open(mini_files[0]) as mini:
            m = yaml.safe_load(mini)
        #
        # Number of segments of each type encountered so far
        #   Could discover from YAML file
        #
        type_counts = {t:0 for t in seg_types}
        for seg in m:
            seg["irregularities"] = []
            #
            # Expand simple time representation in YAML to datetime,
            #   check that the time is during the flight
            #
            for t in ["start", "end"]:
                seg[t] = dict_to_datetime(year, month, day, seg[t])
                # Here's where we should check against takeoff and landing times
                if(seg[t] < takeoff_time or seg[t] > landing_time): print ("oh noes segment ", seg["name"], "seems has bad time")
            #
            # Segment ID is two characters for month, day; includes two character from type.
            #  We're assuming that the segments come in sorted
            #
            if seg["kind"] not in seg_types:
                print ("oh noes I don't understand this segment type")
                seg["segment_id"] = "NULL"
            else:
                type_counts[seg["kind"]] += 1
                seg["segment_id"] = 'P3-{:02d}{:02d}_{}{}'.format(month, day, seg["kind"][0:2], type_counts[seg["kind"]])
            #
            # Rename one attrtibute
            #
            seg["kinds"] = [seg.pop("kind")]
            #
            # Reorder for readaibility
            #
            seg = {s:seg[s] for s in ["kinds", "name", "segment_id", "start", "end", "irregularities"] }

        flight_yaml = p3_info
        flight_yaml.update({'flight_id': 'P3-{:02d}{:02d}'.format(month, day),
                            'name': 'RF{:02d}'.format(flight_dates.index(d) + 1),
                            'events': [],
                            'remarks': [],
                            'date': datetime.date(year, month, day),
                            'flight_report': 'https://observations.ipsl.fr/aeris/eurec4a-data/REPORTS/WP-3D/2020/TO-COME.pdf',
                            'takeoff' : takeoff_time,
                            'landing' : landing_time,
                            'version': data_version,
                            'segments':[seg for seg in m]})

        output_name = seg_dir.joinpath("{}_{}".format(platform, variable) + "_{:04d}{:02d}{:02d}".format(year,month,day) + data_version + ".yaml")
        print ("  Writing to ", output_name)
        with open(output_name, "w") as stream:
            yaml.dump(flight_yaml, stream, default_flow_style=False, sort_keys=False)
