The file 'Nominal_FFA_arc_optics.xlsx' has all of the entrance end optics for all six passes through both the east and west FFA arcs.


What's in the folders:

    The folder 'Old Arcs' contains the arc simulations that I'm not using here anymore: 'baseline nominal' arcs which have no 
    corrector elements, and 'minimal correction' which contains my first pass at radial corrections.
    
    'East Arc with correction' and 'West... correction' contain the current arc hardware and optics files. The tao.init files 
    only have radial orbit data, but the variables to control x and y bending and focusing are included: future updates will 
    include all the required data.

    The folder 'Tao templates' is exactly as it sounds: it has template files 'tao.init' 'tao_plot.init' and 'tao.startup' inside.
    Really just for convenience, that way you (or I, or anyone else) can just copy the initialization files into your lattice folder, 
    modify the pertinent parameters, and it's off to the races.



How to run the lattices (generally):
    2. Download the relevant 'East Arc...' or 'West Arc...' folder
    3. Navigate to that folder from a command line
    4. Type 'tao' at the command prompt and you're in (if you have Bmad installed)

Updates for 2025-07-09:

Three main changes from prior version, for both east and west.
    1. Cells do not start with a drift, to bring initial optics/offset/trajectory more in line with Stephen's spreadsheets (used for vetting).
    2. Absolute value signs have been wrapped around the bending angle of the magnet in the formulas that calculate the geometric offsets.
    3. Apertures have been re-defined to center around the actual orbits.
Minor changes:
    1. Fixed the unscaled dxF and dxD values for the east arc parameters.
    2. I think the original BF x2 aperture that was reported as 0.025 was supposed to be 0.0025, because otherwise the aperture of that magnet was significantly larger - I assumed it was supposed to be 0.0025 when shifting the aperture limits.

Overall, most optics look similar, except that the initial orbit offsets are shifted and the magnetic field seen by the particles is significantly reduced. 
