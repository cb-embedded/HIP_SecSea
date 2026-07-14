# HIP_SecSea
Hack In Provence badge for SecSea

## Changes from V1.1 (@chris_cannes)

This version is based on the V1.1 design by @chris_cannes. The following changes were made:

**Antenna area**
- Antenna placement and copper zones reworked to comply with CC1101 datasheet requirements.
- Replaced four independent copper cutout polygons with a proper keepout zone (larger, as required by the doc).

**Layer stackup**
- Added a dedicated Ground plane (inner layer).
- Added a dedicated 3.3V Power plane (inner layer).
- Main routing moved to Top and Bottom layers.

**Power distribution**
- The 3.3V distribution tree replaced by a solid 3.3V power plane.

**GND stitching**
- Stitching vias replaced by GND vias placed as close as possible to GND pads, connecting directly into the ground plane. This ensures a controlled, low-impedance GND return path.

## TODO (before production)

- [ ] Rebuild copper planes and stitching vias: add back a proper grid of stitching vias (perimeter, around RF keepout zone, under CC1101) in addition to the pad-level GND vias.

