These files are those used to develop the BMAD spreader files. Errors are likely.

To run these, load them with the appropriate init file:

tao -lat Pass*_Test.bmad -init tao_p*.init

* is the pass number.

From here, you have two options:

1. Use the files "as is," which uses the optimization files relevant to each pass. For example, you'll see the line "call p*.out" written near the bottom of each lattice file. Those files use settings based on the optimizations written in the appropriate initialization file. If you just want to run, this is the simple option.

2. You can then further optimize by typing "run lmdif" in the terminal. However, if you want to start from scratch, comment out the line in the .bmad file where it calls the optimization output file, and run from there.

Furthermore, the FFA passes (9, 11, 13, 15, 17,and 19) have two lines calling optimization files. If you want everything optimized for that individual pass, then use the pass number corresponding to the pass. If you want to use the values from pass 9, then uncomment that line, comment the other call line, and load. 

Please note that each FFA pass cannot be realistically optimized in the way that they currently are. This is part of the "test" of these files. This is *not* correct.

It is also important to point out that offsets for each pass have not been written into the septa yet. For now, each FFA pass assumes no offset for the septa, and a central entrance/exit. This is also not correct.

Recall that the NE spreader is in the East arc, and therefore only sees "odd" passes: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19.
