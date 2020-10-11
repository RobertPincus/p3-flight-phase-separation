#! /usr/bin/env python
#
# A script to expand minimal YAML files descirbing only the segments from a P3 research flight
#    during ATOMIC by category, name, time and window (start, end) into more complete
#   YAML files following the conventions used by HALO during EUREC4A
#   (https://github.com/eurec4a/halo-flight-phase-separation)
#
# Takeoff and landing times are inferred from the flight-level summary file in a simple way
#   Segment time windows are checked against the flight times
# Segment IDs are created in the order the segments are provided in the mini-yaml file.
#
# Contact: Robert Pincus <Robert.Pincus@colorado.edu>
#
import datetime
import yaml
import pathlib
from intake import open_catalog

import xarray as xr

cat_dir  = pathlib.Path('/Users/robert/Dropbox/Scientific/Papers/ATOMIC-P3-data/Figures/p3-intake-catalog/')
seg_dir  = pathlib.Path('./flight_phase_files')
mini_dir = pathlib.Path('./mini-yaml')
mini_prefix = "flight-phase-mini"


campaign = "EUREC4A"
project  = "ATOMIC"
platform = "P3"
variable = "Flight-segments"
data_version = "v0.5"

#
# Controlled vocabulary for segment types - the script will complain if a segment has a different kind.
#
valid_seg_types = ['transit', 'circle', 'profile', 'axbt', 'cloud']
include_seg_types = valid_seg_types # ['circle']
#
# .
#
flight_dates = [datetime.date(2020, 1, 17),
                datetime.date(2020, 1, 19),
                datetime.date(2020, 1, 23),
                datetime.date(2020, 1, 24),
                datetime.date(2020, 1, 31),
                datetime.date(2020, 2,  3),
                datetime.date(2020, 2,  4),
                datetime.date(2020, 2,  5),
                datetime.date(2020, 2,  9),
                datetime.date(2020, 2, 10),
                datetime.date(2020, 2, 11)]


p3_info = {'campaign':'EUREC4A', 'project':'ATOMIC', 'platform':'P3',
           "contacts": [{'name': 'Robert Pincus',
                        'email': 'Robert.Pincus@colorado.edu',
                        'tags': ['sc', 'dp']},
                        {'name': 'Adriana Bailey',
                        'email': 'abailey@ucar.edu',
                        'tags': ['sc', 'dp']},
                        {'name': 'Chris Fairall',
                        'email': 'Chris.Fairall@noaa.gov',
                        'tags': ['cs', 'pi']}] }

def date_to_datetime(d, tm):
    # '''Here tm is a dict with keys hour, min, and optinally sec'''
    if 'sec' in tm.keys():
        return(datetime.datetime(d.year, d.month, d.day, hour=int(tm["hour"]), minute=int(tm["min"]), second=int(tm["sec"])))
    else:
        return(datetime.datetime(d.year, d.month, d.day, hour=int(tm["hour"]), minute=int(tm["min"])))

if __name__ == "__main__":
    print("Processing " + mini_prefix + " mini yaml files")
    p3data = open_catalog(str(cat_dir.joinpath('main.yaml')))
    for d in flight_dates:
        #
        # Flight level summary file - could construct name/URL more programatically
        #
        f = p3data.flight_level[d.strftime("P3-%m%d")].to_dask()
        #
        # Take-off and landing times, approach suggested by Adriana Bailey
        #
        in_air = f.where(f.alt > 80., drop=True)
        # Convert from np.datetime64 to datetime.datetimes
        takeoff_time = in_air.time[ 0].values.astype('datetime64[s]').tolist()
        landing_time = in_air.time[-1].values.astype('datetime64[s]').tolist()

        mini_files = sorted(mini_dir.glob(mini_prefix + d.strftime('-%Y-%m-%d') + "*.yaml"))
        if len(mini_files) is 0:
            print ("Mini YAML file missing, skipping date " + d.strftime('%Y-%m-%d'))
        else:
            print('Flight RF{:02d}'.format(flight_dates.index(d) + 1))
            print("  nominal takeoff time", takeoff_time, "nominal landing time", landing_time)
            with open(mini_files[0]) as mini:
                m = yaml.safe_load(mini)
            #
            # Number of segments of each type encountered so far
            #   Could discover from YAML file
            #
            type_counts = {t:0 for t in valid_seg_types}
            for seg in m:
                seg["irregularities"] = []
                #
                # Expand simple time representation in YAML to datetime,
                #   check that the time is during the flight
                #
                for t in ["start", "end"]:
                    seg[t] = date_to_datetime(d, seg[t])
                    # Here's where we should check against takeoff and landing times
                    if(seg[t] < takeoff_time or seg[t] > landing_time): print ("oh noes segment ", seg["name"], "seems has bad time")
                #
                # Segment ID is two characters for month, day; includes two character from type.
                #  We're assuming that the segments come in sorted
                #
                if seg["kind"] not in valid_seg_types:
                    print ("oh noes I don't understand segment type ", seg["kind"])
                    seg["segment_id"] = "NULL"
                else:
                    type_counts[seg["kind"]] += 1
                    seg["segment_id"] = 'P3-{:02d}{:02d}_{}{}'.format(d.month, d.day, seg["kind"][0:2], type_counts[seg["kind"]])
                #
                # Rename one attrtibute
                #
                seg["kinds"] = [seg.pop("kind")]
                #
                # Reorder for readaibility
                #
                seg = {s:seg[s] for s in ["kinds", "name", "segment_id", "start", "end", "irregularities"] }

            flight_yaml = p3_info
            flight_yaml.update({'flight_id': d.strftime("P3-%m%d"),
                                'name': 'RF{:02d}'.format(flight_dates.index(d) + 1),
                                'events': [],
                                'remarks': [],
                                'date': d,
                                'flight_report': 'https://observations.ipsl.fr/aeris/eurec4a-data/REPORTS/WP-3D/2020/TO-COME.pdf',
                                'takeoff' : takeoff_time,
                                'landing' : landing_time,
                                'version': data_version,
                                'segments':[seg for seg in m if seg["kinds"][0] in include_seg_types]})

            output_name = seg_dir.joinpath("{}_{}_{}_{}".format(campaign, project, platform, variable) +
                                           d.strftime("_%Y%m%d") + "_" + data_version + ".yaml")
            print ("  Writing to ", output_name)
            with open(output_name, "w") as stream:
                yaml.dump(flight_yaml, stream, default_flow_style=False, sort_keys=False)
            print()
