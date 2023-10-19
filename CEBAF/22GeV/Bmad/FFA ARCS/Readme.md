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

