
# Flight segmentation for the NOAA P3 during ATOMIC/EUREC4A

This repository provides files describing the different segments or phases of eleven research flights made by the NOAA P3
during the Atlantic Ocean-atmosphere Mesoscale Interaction Campaign, ATOMIC. It follows the
[flight phase separation for HALO](https://github.com/eurec4a/halo-flight-phase-separation) made for the broader EUREC4A experiement.

## Top level segments

Flight will be broadly described using four types of segments

### profile
- Long ascents or descents, typically at constant heading and nearly constant ascent or descent rate

### AXBT
- A series of straight and level legs, flown at 9000-10000 ft/2.75-3 km, from which AXBTs were deployed.

### cloud
- A series of level legs, typically from near the surface to above cloud tops, interspersed with altitude changes

### circle:
- Um, when the plane is flying in a circle. Normally it's dropping sondes.

### transit:
- Times when the aircraft was not actively engaged in scientific sampling. Some legs may nonetheless provide useful data

## Supersets

Following the HALO flight phase separation we include the label

#### circling:
- An overarching term indicating multiple circles made in a row.

## Subsets

All segments, but especially `cloud` and `transit` segments, may also include

#### level:
- Legs in which aircraft altitude varies minimally

### cline
- Legs in which the aircraft is actively ascending or descending

For the moment we are creating the flight_phase_files by hand. They should be processed with the `scripts/utils/attach_sondes.py` from the HALO flight phase repo to incorporate the dropsondes from JOANNE. Probably we create AXBT IDs to mirror the sonde IDs and include those too.

Takeoff and landing times need revision in the files.
