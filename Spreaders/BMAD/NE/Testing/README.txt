These files are those used to develop the BMAD spreader files. Errors are likely.

To run these, load them with the appropriate init file:

tao -lat Pass*_Test.bmad -init tao_p*.init

* is the pass number.

Once you load the file(s), you should type "run lmdif" in the terminal to run the optimizations needed to get the files correct. Once you run this, you can see the various values of elements, optics, etc...

Recall that the NE spreader is in the East arc, and therefore only sees "odd" passes: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19.
