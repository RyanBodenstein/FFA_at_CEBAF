The file 'Nominal_FFA_arc_optics.xlsx' has all of the entrance end optics for all six passes through both the east and west FFA arcs.


What's in the folders:

    The folder 'Baseline Nominal' contains - as you may have guessed - the exactly nominal designs for six passes through the east and west arc.
    No errors, no correctors, nothing at al other than that sweet sweet perfect machine.

    The folder 'Minimal Correctors' contains the east and west arcs (6 passes each) preconfigured to do horizontal orbit corrections: 
    the lattices don't have errors yet, but you may impose them according to the instructions in that folder.
    The folder is called 'Minimal' because there is only one corrector and one BPM per cell. This handles girder offsets just fine, but I haven't really experimented with changing starting coordinates for those lattices yet. It's on my list and I'll let you know soon.
    Vertical beam corrections and optics corrections are possible, but I haven't added the diagnostics needed (because I'm lazy):
    they'll come soon too.

    The folder 'Tao templates' is exactly as it sounds: it has template files 'tao.init' 'tao_plot.init' and 'tao.startup' inside.
    Really just for convenience, that way you (or I, or anyone else) can just copy the initialization files into your lattice folder, 
    modify the pertinent parameters, and it's off to the races.

    I'm not gonna tell you about 'Testing.' Unless your name is Alexander Mattison Coxe, you got no business in there.


How to run the lattices (generally):
    1. Pick your favorite part of the machine: east, west, nominal, corrected, you name it
    2. Download the relevant 'East Arc' or 'West Arc' folder
    3. Navigate to that folder from a command line
    4. Type 'tao' at the command prompt and you're in (if you have Bmad installed)

The correction lattices have a little bit more doc in that folder.
Again: if you try to run something from 'Testing' I take no responsibility for what happens.
    Your computer is unlikely to break, but something almost certainly won't work and you won't find what you're looking for.