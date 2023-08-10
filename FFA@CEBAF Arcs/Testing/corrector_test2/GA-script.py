# GA-script.py
# this script opens tao,
# tells whether the beam makes it through,
# gives an option to run an optimizer,
# then returns end[x,px]
# written per Balsa's request
# for use with genetic algorithm tools

# import statements
import pytao
from pytao import Tao

# import matplotlib as mpl
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# define some constants to make life livable
in1 = 'python data_parameter '
taodx = 'python data_parameter orbit.bpm1x[7] design_value'
taomx = 'python data_parameter orbit.bpm1.x[7] model_value'
taodpx = 'python data_parameter orbit.bpm1px[7] design_value'
taompx = 'python data_parameter orbit.bpm1px[7] model_value'




tao = Tao("-init tao.init -noplot") # initialize Tao in this folder

# desx and despx are the design values of x and px, respectively at lattice end
desx = float(tao.cmd(taodx, raises=False)[0].lstrip('1;'))
despx = float(tao.cmd(taodpx, raises=False)[0].lstrip('1;'))

check = float(tao.cmd(taomx, raises=False)[0].lstrip('1;')) # if check = 0, the beam was lost

count = 0 # count the number of iterations

# function
# that reads the model values of the orbit
# and tries to make sure the beam makes it through the lattice
def passed(chk):
    if (chk == 0): # if the beam is lost and we haven't exceeded recursion depth
        print('Beam did not make it through the lattice, running local optimizers')
        tao.cmd('run lm', raises=False) # run the lm optimizer, calculates derivatives
        tao.cmd('run lmdif', raises=False) # run lmdif optimizer, no recalculation
        chk = float(tao.cmd(taomx)[0].lstrip('1;')) # redefine input value
        return chk
    elif(chk > 0): # if we made it through the lattice in time
        xout = float(tao.cmd(taomx, raises=False)[0].lstrip('1;')) # get exit x
        pxout = float(tao.cmd(taompx, raises=False)[0].lstrip('1;')) # get exit px
        print('At the exit, x = ',xout,'and px = ',pxout)
        print('These differ from design values by Δx = ', xout - desx,'and Δpx = ',pxout-despx)
        print('After ',count,' optimizations.')
        return chk
    else: # if we exceed recursion depth\
        print("Optimizations couldn't fix the beam loss")
        return chk
    
while (count < 10):
    check = passed(check)
    if (check > 0): break

    
